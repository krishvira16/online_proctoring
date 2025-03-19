import dataclasses
from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from typing import Annotated, Optional

from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase, Mapped, mapped_column, relationship, composite


int_pk = Annotated[int, mapped_column(primary_key=True)]

class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[int_pk] = mapped_column(init=False)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    _: KW_ONLY
    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    
    test_setter_role: Mapped[Optional['TestSetter']] = relationship(default=None, cascade='all, delete-orphan')
    test_taker_role: Mapped[Optional['TestTaker']] = relationship(default=None, cascade='all, delete-orphan')
    invigilator_role: Mapped[Optional['Invigilator']] = relationship(default=None, cascade='all, delete-orphan')

class TestSetter(Base, kw_only=True):
    __tablename__ = 'test_setter'

    id: Mapped[int_pk] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), init=False)
    created_tests: Mapped[list['Test']] = relationship(back_populates='creator', default_factory=list)

class TestTaker(Base, kw_only=True):
    __tablename__ = 'test_taker'

    id: Mapped[int_pk] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), init=False)
    test_attempts: Mapped[list['TestAttempt']] = relationship(back_populates='test_taker', cascade='all, delete-orphan')

class Invigilator(Base, kw_only=True):
    __tablename__ = 'invigilator'

    id: Mapped[int_pk] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), init=False)
    invigilations: Mapped[list['TestAttempt']] = relationship(back_populates='invigilator')

class Test(Base, kw_only=True):
    __tablename__ = 'test'
    
    id: Mapped[int_pk] = mapped_column(init=False)
    title: Mapped[str]
    description: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    guidelines: Mapped[str]
    questions: Mapped[list['Question']] = relationship(cascade='all, delete-orphan')
    
    creator_id: Mapped[int] = mapped_column(ForeignKey("test_setter.id"), init=False)
    creator: Mapped[TestSetter] = relationship(back_populates="created_tests")
    
    attempts: Mapped[list['TestAttempt']] = relationship(back_populates='test', cascade='all, delete-orphan', default_factory=list)

    @property
    def max_marks(self) -> int:
        return sum(q.max_marks for q in self.questions)

class Question(Base, kw_only=True):
    __tablename__ = 'question'
    
    id: Mapped[int_pk] = mapped_column(init=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("test.id", ondelete='CASCADE'), init=False)
    question_text: Mapped[str]
    multiple_choice_question: Mapped[Optional['MultipleChoiceQuestion']] = relationship(default=None, cascade='all, delete-orphan')
    text_field_question: Mapped[Optional['TextFieldQuestion']] = relationship(default=None, cascade='all, delete-orphan')
    attachment_question: Mapped[Optional['AttachmentQuestion']] = relationship(default=None, cascade='all, delete-orphan')
    max_marks: Mapped[int]
    
    answer_attempts: Mapped[list['Answer']] = relationship(back_populates='question', cascade='all, delete-orphan', default_factory=list)

class MultipleChoiceQuestion(Base, kw_only=True):
    __tablename__ = 'multiple_choice_question'
    
    id: Mapped[int_pk] = mapped_column(ForeignKey('question.id', ondelete='CASCADE'), init=False)
    options: Mapped[list['Option']] = relationship(foreign_keys='[Option.question_id]', cascade='all, delete-orphan')
    correct_option_id: Mapped[None | int] = mapped_column(init=False)
    correct_option: Mapped['Option'] = relationship(
        foreign_keys='[MultipleChoiceQuestion.id, MultipleChoiceQuestion.correct_option_id]', 
        post_update=True, 
        overlaps="multiple_choice_question"
    )
    __table_args__ = ForeignKeyConstraint(
        columns=['id', 'correct_option_id'],
        refcolumns=['option.question_id', 'option.id'],
        name='multiple_choice_question_id_correct_option_id_fkey',
        use_alter=True,
    ),

class Option(Base):
    __tablename__ = 'option'
    
    id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("multiple_choice_question.id", ondelete='CASCADE'), init=False)
    __table_args__ = UniqueConstraint('id', 'question_id'),
    option_text: Mapped[str]

class TextFieldQuestion(Base):
    __tablename__ = 'text_field_question'

    id: Mapped[int_pk] = mapped_column(ForeignKey('question.id', ondelete='CASCADE'), init=False)

class AttachmentQuestion(Base):
    __tablename__ = 'attachment_question'

    id: Mapped[int_pk] = mapped_column(ForeignKey('question.id', ondelete='CASCADE'), init=False)

@dataclass
class Point:
    x: float
    y: float

@dataclass(kw_only=True)
class Rectangle:
    top_left: Point
    top_right: Point
    bottom_left: Point
    bottom_right: Point
    
    @classmethod
    def _generate(
        cls, 
        top_left_x: float, top_left_y: float,
        top_right_x: float, top_right_y: float,
        bottom_left_x: float, bottom_left_y: float,
        bottom_right_x: float, bottom_right_y: float
    ) -> 'Rectangle':
        """generate an object from a database row"""
        return Rectangle(
            top_left=Point(top_left_x, top_left_y), 
            top_right=Point(top_right_x, top_right_y), 
            bottom_left=Point(bottom_left_x, bottom_left_y), 
            bottom_right=Point(bottom_right_x, bottom_right_y)
        )

    def __composite_values__(self) -> tuple[float, ...]:
        """generate a database row from an object"""
        return (
            dataclasses.astuple(self.top_left) 
            + dataclasses.astuple(self.top_right)
            + dataclasses.astuple(self.bottom_left) 
            + dataclasses.astuple(self.bottom_right)
        )

class TestAttempt(Base, kw_only=True):
    __tablename__ = 'test_attempt'
    
    id: Mapped[int_pk] = mapped_column(init=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("test.id", ondelete='CASCADE'), init=False)
    test: Mapped[Test] = relationship(back_populates="attempts")
    test_taker_id: Mapped[int] = mapped_column(ForeignKey("test_taker.id", ondelete='CASCADE'), init=False)
    test_taker: Mapped[TestTaker] = relationship(back_populates="test_attempts", foreign_keys='[TestAttempt.test_taker_id]')
    __table_args__ = UniqueConstraint('test_id', 'test_taker_id'),
    invigilator_id: Mapped[int] = mapped_column(ForeignKey("invigilator.id"), init=False)
    invigilator: Mapped[Invigilator] = relationship(back_populates='invigilations', foreign_keys='[TestAttempt.invigilator_id]')
    environment_image_url: Mapped[str]
    top_left_x: Mapped[float]
    top_left_y: Mapped[float]
    top_right_x: Mapped[float]
    top_right_y: Mapped[float]
    bottom_left_x: Mapped[float]
    bottom_left_y: Mapped[float]
    bottom_right_x: Mapped[float]
    bottom_right_y: Mapped[float]
    screen_position: Mapped[Rectangle] = composite(
        Rectangle._generate,
        'top_left_x', 'top_left_y',
        'top_right_x', 'top_right_y',
        'bottom_left_x', 'bottom_left_y',
        'bottom_right_x', 'bottom_right_y'
    )
    start_time: Mapped[None | datetime]
    answers: Mapped[list['Answer']] = relationship(back_populates='test_attempt', cascade='all, delete-orphan')
    end_time: Mapped[None | datetime]

    @property
    def marks_obtained(self) -> None | int:
        if any(answer.marks_obtained is None for answer in self.answers):
            return None
        else:
            return sum(answer.marks_obtained for answer in self.answers) # type: ignore

    gaze_data: Mapped[list['GazeData']] = relationship(back_populates='test_attempt', cascade='all, delete-orphan')
    caught_cheating: Mapped[bool]

class Answer(Base, kw_only=True):
    __tablename__ = 'answer'
    
    test_attempt_id: Mapped[int_pk] = mapped_column(ForeignKey("test_attempt.id", ondelete='CASCADE'), init=False)
    test_attempt: Mapped[TestAttempt] = relationship(back_populates="answers")
    question_id: Mapped[int_pk] = mapped_column(ForeignKey("question.id", ondelete='CASCADE'), init=False)
    question: Mapped[Question] = relationship(back_populates="answer_attempts")
    mcq_answer: Mapped[Optional['MCQAnswer']] = relationship(cascade='all, delete-orphan')
    text_field_answer: Mapped[Optional['TextFieldAnswer']] = relationship(cascade='all, delete-orphan')
    attachment_answer: Mapped[Optional['AttachmentAnswer']] = relationship(cascade='all, delete-orphan')
    marks_obtained: Mapped[None | int]
    is_bookmarked: Mapped[bool] = mapped_column(default=False)

class MCQAnswer(Base):
    __tablename__ = 'mcq_answer'

    test_attempt_id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[int_pk] = mapped_column(init=False)
    chosen_option_id: Mapped[Optional[int]] = mapped_column(init=False)
    chosen_option: Mapped[Optional[Option]] = relationship(default=None, overlaps="mcq_answer")
    __table_args__ = (
        ForeignKeyConstraint(columns=['test_attempt_id', 'question_id'], refcolumns=['answer.test_attempt_id', 'answer.question_id'], ondelete='CASCADE'),
        ForeignKeyConstraint(columns=['question_id'], refcolumns=['multiple_choice_question.id']),
        ForeignKeyConstraint(columns=['question_id', 'chosen_option_id'], refcolumns=['option.question_id', 'option.id']),
    )

class TextFieldAnswer(Base):
    __tablename__ = 'text_field_answer'

    test_attempt_id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[int_pk] = mapped_column(init=False)
    __table_args__ = (
        ForeignKeyConstraint(columns=['test_attempt_id', 'question_id'], refcolumns=['answer.test_attempt_id', 'answer.question_id'], ondelete='CASCADE'),
        ForeignKeyConstraint(columns=['question_id'], refcolumns=['text_field_question.id']),
    )
    answer_text: Mapped[str] = mapped_column(default='')

class AttachmentAnswer(Base):
    __tablename__ = 'attachment_answer'

    test_attempt_id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[int_pk] = mapped_column(init=False)
    __table_args__ = (
        ForeignKeyConstraint(columns=['test_attempt_id', 'question_id'], refcolumns=['answer.test_attempt_id', 'answer.question_id'], ondelete='CASCADE'),
        ForeignKeyConstraint(columns=['question_id'], refcolumns=['attachment_question.id']),
    )
    attached_file_url: Mapped[Optional[str]] = mapped_column(default=None)

class GazeData(Base):
    __tablename__ = 'gaze_data'
    
    id: Mapped[int_pk] = mapped_column(init=False)
    test_attempt_id: Mapped[int] = mapped_column(ForeignKey("test_attempt.id", ondelete='CASCADE'), init=False)
    test_attempt: Mapped[TestAttempt] = relationship(back_populates="gaze_data")
    timestamp: Mapped[datetime]
    gaze_extrapolation: Mapped[Point] = composite(mapped_column('x'), mapped_column('y'))