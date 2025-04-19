from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Optional, Self
from quart import Blueprint, Response, current_app
from quart_schema import validate_request, validate_response

from ...data_model import AttachmentQuestion, MultipleChoiceQuestion, Question, Test, TestSetter, TextFieldQuestion
from ...database import get_orm_session, orm_session
from ...error_handling import APIError
from ..user.authentication import authentication_required, ensure_authenticated, get_current_user, current_user


bp = Blueprint('test_setter', __name__, url_prefix='/test_setter')
bp.before_request(ensure_authenticated)

@bp.post('/assume_role')
async def assume_role():
    current_user = get_current_user()
    if await current_user.awaitable_attrs.test_setter_role is not None:
        raise APIError(400, 'User is already a test setter.')
    current_user.test_setter_role = TestSetter()
    await orm_session.commit()
    return Response(status=204)

@authentication_required
async def require_test_setter_role():
    if await current_user.awaitable_attrs.test_setter_role is None:
        raise APIError(403, 'Forbidden')
    
def test_setter_role_required[T, **P](func: Callable[P, Awaitable[T]] | Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        await require_test_setter_role()
        return await current_app.ensure_async(func)(*args, **kwargs) # type: ignore
    return wrapper

core_bp = Blueprint('test_setter_core', __name__)
core_bp.before_request(require_test_setter_role)
bp.register_blueprint(core_bp)

@dataclass
class TestDetails:
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    guidelines: str
    questions: 'list[QuestionDetails]'

    @classmethod
    async def from_structural_superset(cls, test: Test) -> Self:
        return cls(
            id=test.id,
            title=test.title,
            description=test.description,
            start_time=test.start_time,
            end_time=test.end_time,
            guidelines=test.guidelines,
            questions=[
                await QuestionDetails.from_structural_superset(question)
                for question in await test.awaitable_attrs.questions
            ]
        )

@dataclass
class QuestionDetails:
    discriminator: int
    question_text: str
    max_marks: int
    multiple_choice_question: 'Optional[MultipleChoiceQuestionDetails]' = None
    text_field_question: 'Optional[TextFieldQuestionDetails]' = None
    attachment_question: 'Optional[AttachmentQuestionDetails]' = None

    @classmethod
    async def from_structural_superset(cls, question: Question) -> Self:
        return cls(
            discriminator=question.id.discriminator,
            question_text=question.question_text,
            max_marks=question.max_marks,
            multiple_choice_question=(
                await MultipleChoiceQuestionDetails.from_structural_superset(mcq)
                if (mcq:= await question.awaitable_attrs.multiple_choice_question) is not None
                else None
            ),
            text_field_question=(
                TextFieldQuestionDetails.from_structural_superset(tfq)
                if (tfq:= await question.awaitable_attrs.text_field_question) is not None
                else None
            ),
            attachment_question=(
                AttachmentQuestionDetails.from_structural_superset(aq)
                if (aq:= await question.awaitable_attrs.attachment_question) is not None
                else None
            )
        )

@dataclass
class MultipleChoiceQuestionDetails:
    options: 'list[OptionDetails]'
    correct_option_discriminator: int

    @classmethod
    async def from_structural_superset(cls, mcq: MultipleChoiceQuestion) -> Self:
        return cls(
            options=[
                OptionDetails.from_structural_superset(option)
                for option in await mcq.awaitable_attrs.options
            ],
            correct_option_discriminator=mcq.correct_option_discriminator # type: ignore
        )

@dataclass
class OptionDetails:
    discriminator: int
    option_text: str

    @classmethod
    def from_structural_superset(cls, option: MultipleChoiceQuestion.Option) -> Self:
        return cls(
            discriminator=option.id.discriminator,
            option_text=option.option_text
        )

@dataclass
class TextFieldQuestionDetails:
    @classmethod
    def from_structural_superset(cls, tfq: TextFieldQuestion) -> Self:
        return cls()

@dataclass
class AttachmentQuestionDetails:
    @classmethod
    def from_structural_superset(cls, aq: AttachmentQuestion) -> Self:
        return cls()

@core_bp.get('/tests')
@validate_response(list[TestDetails])
async def get_tests():
    tests = await current_user.test_setter_role.awaitable_attrs.created_tests # type: ignore
    return [await TestDetails.from_structural_superset(test) for test in tests]

@core_bp.post('/create_test')
@validate_request(TestDetails)
async def create_test(data: TestDetails):
    test = Test(
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        guidelines=data.guidelines,
        questions=[
            Question(
                question_text=question.question_text,
                max_marks=question.max_marks,
                multiple_choice_question=MultipleChoiceQuestion(
                    options=(options:= [
                        MultipleChoiceQuestion.Option(option_text=option.option_text)
                        for option in question.multiple_choice_question.options
                    ]),
                    correct_option=options[
                        [option.discriminator for option in question.multiple_choice_question.options]
                        .index(question.multiple_choice_question.correct_option_discriminator)
                    ]
                ) 
                if question.multiple_choice_question is not None else None,
                text_field_question=TextFieldQuestion() if question.text_field_question is not None else None,
                attachment_question=AttachmentQuestion() if question.attachment_question is not None else None
            )
            for question in data.questions
        ],
        creator=current_user.test_setter_role # type: ignore
    )
    orm_session = get_orm_session()
    orm_session.add(test)
    await orm_session.commit()
    return Response(status=204)