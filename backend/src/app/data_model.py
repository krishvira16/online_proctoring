import dataclasses
from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from typing import Annotated, Optional

from sqlalchemy import DateTime, Float, ForeignKey, ForeignKeyConstraint, Integer, Text, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase, Mapped, mapped_column, relationship, composite, attribute_keyed_dict, WriteOnlyMapped


int_pk = Annotated[int, mapped_column(primary_key=True)]

def get_id_columns(mapped_class):
    return mapped_class.id.property.props

class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }

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
    test_attempts: Mapped[dict[int, 'TestAttempt']] = relationship(
        cascade='all, delete-orphan',
        default_factory=dict, collection_class=attribute_keyed_dict('test_id'),
    )

class Invigilator(Base, kw_only=True):
    __tablename__ = 'invigilator'

    id: Mapped[int_pk] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), init=False)
    invigilations: Mapped[list['TestAttempt']] = relationship(back_populates='invigilator', default_factory=list)

class Test(Base, kw_only=True):
    __tablename__ = 'test'
    
    id: Mapped[int_pk] = mapped_column(init=False)
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    guidelines: Mapped[str] = mapped_column(Text)
    questions: Mapped[list['Question']] = relationship(
        cascade='all, delete-orphan',
        order_by='Question.number', collection_class=ordering_list('number', reorder_on_append=True),
    )
    
    creator_id: Mapped[int] = mapped_column(ForeignKey('test_setter.id'), init=False)
    creator: Mapped[TestSetter] = relationship(back_populates='created_tests')
    
    attempts: Mapped[dict[int, 'TestAttempt']] = relationship(
        cascade='all, delete-orphan',
        default_factory=dict, collection_class=attribute_keyed_dict('test_taker_id'),
    )

    @property
    def max_marks(self) -> int:
        return sum(q.max_marks for q in self.questions)

class Question(Base, kw_only=True):
    __tablename__ = 'question'

    @dataclass(frozen=True)
    class Id:
        test_id: int
        discriminator: int
    
    id: Mapped[Id] = composite(
        mapped_column('test_id', ForeignKey('test.id', ondelete='CASCADE'), primary_key=True), 
        mapped_column('discriminator', autoincrement=True, primary_key=True), 
        init=False,
    )
    number: Mapped[int] = mapped_column(init=False)
    __table_args__ = (
        UniqueConstraint(
            'test_id', number,
            name='question_number_uq',
            deferrable=True, initially='DEFERRED',
        ),
    )
    question_text: Mapped[str] = mapped_column(Text)
    multiple_choice_question: Mapped[Optional['MultipleChoiceQuestion']] = relationship(cascade='all, delete-orphan', default=None)
    text_field_question: Mapped[Optional['TextFieldQuestion']] = relationship(cascade='all, delete-orphan', default=None)
    attachment_question: Mapped[Optional['AttachmentQuestion']] = relationship(cascade='all, delete-orphan', default=None)
    max_marks: Mapped[int]
    
    answer_attempts: Mapped[list['Answer']] = relationship(back_populates='question', cascade='all, delete-orphan', default_factory=list)

class MultipleChoiceQuestion(Base, kw_only=True):
    __tablename__ = 'multiple_choice_question'
    
    id: Mapped[Question.Id] = composite(
        mapped_column('test_id', primary_key=True),
        mapped_column('discriminator', primary_key=True),
        init=False,
    )
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'discriminator'],
            refcolumns=get_id_columns(Question),
            ondelete='CASCADE',
        ),
    )

    class Option(Base):
        __tablename__ = 'option'
        
        @dataclass(frozen=True)
        class Id:
            multiple_choice_question_id: Question.Id
            discriminator: int

            @classmethod
            def _generate(cls, test_id: int, question_discriminator: int, discriminator: int) -> 'MultipleChoiceQuestion.Option.Id':
                """generate an object from a database row"""
                return MultipleChoiceQuestion.Option.Id(Question.Id(test_id, question_discriminator), discriminator)
            
            def __composite_values__(self) -> tuple[int, int, int]:
                """generate a database row from an object"""
                return dataclasses.astuple(self.multiple_choice_question_id) + (self.discriminator,)
        
        id: Mapped[Id] = composite(
            Id._generate,
            mapped_column('test_id', Integer, primary_key=True),
            mapped_column('question_discriminator', Integer, primary_key=True),
            mapped_column('discriminator', Integer, autoincrement=True, primary_key=True),
            init=False,
        )
        number: Mapped[int] = mapped_column(init=False)
        __table_args__ = (
            UniqueConstraint(
                'test_id', 'question_discriminator', number,
                name='option_number_uq',
                deferrable=True, initially='DEFERRED',
            ),
            ForeignKeyConstraint(
                columns=['test_id', 'question_discriminator'],
                refcolumns=['multiple_choice_question.test_id', 'multiple_choice_question.discriminator'],
                ondelete='CASCADE',
            ),
        )
        option_text: Mapped[str] = mapped_column(Text)
    
    options: Mapped[list[Option]] = relationship(
        foreign_keys='[Option.test_id, Option.question_discriminator]',
        cascade='all, delete-orphan',
        order_by='Option.number', collection_class=ordering_list('number', reorder_on_append=True),
    )
    correct_option_discriminator: Mapped[None | int] = mapped_column(init=False)
    correct_option: Mapped[Option] = relationship(
        foreign_keys='[MultipleChoiceQuestion.test_id, MultipleChoiceQuestion.discriminator, MultipleChoiceQuestion.correct_option_discriminator]', 
        post_update=True, 
        overlaps='multiple_choice_question',
        passive_deletes='all',
    )
    __table_args__ += (
        ForeignKeyConstraint(
            columns=['test_id', 'discriminator', 'correct_option_discriminator'],
            refcolumns=get_id_columns(Option),
            name='multiple_choice_question_correct_option_fkey',
            use_alter=True,
            deferrable=True, initially='DEFERRED',
        ),
    )

class TextFieldQuestion(Base):
    __tablename__ = 'text_field_question'

    id: Mapped[Question.Id] = composite(
        mapped_column('test_id', primary_key=True),
        mapped_column('discriminator', primary_key=True),
        init=False,
    )
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'discriminator'],
            refcolumns=get_id_columns(Question),
            ondelete='CASCADE',
        ),
    )

class AttachmentQuestion(Base):
    __tablename__ = 'attachment_question'

    id: Mapped[Question.Id] = composite(
        mapped_column('test_id', primary_key=True),
        mapped_column('discriminator', primary_key=True),
        init=False,
    )
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'discriminator'],
            refcolumns=get_id_columns(Question),
            ondelete='CASCADE',
        ),
    )

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
    
    @dataclass(frozen=True)
    class Id:
        test_id: int
        test_taker_id: int
    test_id: Mapped[int_pk] = mapped_column(ForeignKey('test.id', ondelete='CASCADE'), init=False)
    test_taker_id: Mapped[int_pk] = mapped_column(ForeignKey('test_taker.id', ondelete='CASCADE'), init=False)
    id: Mapped[Id] = composite(test_id, test_taker_id, init=False)

    invigilator_id: Mapped[int] = mapped_column(ForeignKey('invigilator.id'), init=False)
    invigilator: Mapped[Invigilator] = relationship(back_populates='invigilations', foreign_keys='[TestAttempt.invigilator_id]')
    environment_image_url: Mapped[str]
    screen_position: Mapped[Rectangle] = composite(
        Rectangle._generate,
        mapped_column('top_left_x', Float), mapped_column('top_left_y', Float),
        mapped_column('top_right_x', Float), mapped_column('top_right_y', Float),
        mapped_column('bottom_left_x', Float), mapped_column('bottom_left_y', Float),
        mapped_column('bottom_right_x', Float), mapped_column('bottom_right_y', Float)
    )
    start_time: Mapped[None | datetime] = mapped_column(default=None)
    answers: Mapped[dict[Question.Id, 'Answer']] = relationship(
        cascade='all, delete-orphan',
        default_factory=dict, collection_class=attribute_keyed_dict('question_id'),
        overlaps='answer_attempts, question',
    )
    end_time: Mapped[None | datetime] = mapped_column(default=None)

    @property
    def marks_obtained(self) -> None | int:
        if any(answer.marks_obtained is None for answer in self.answers.values()):
            return None
        else:
            return sum(answer.marks_obtained for answer in self.answers.values()) # type: ignore

    gaze_data: WriteOnlyMapped['GazeData'] = relationship(passive_deletes=True, cascade='all, delete-orphan', init=False)
    caught_cheating: Mapped[bool] = mapped_column(default=False)

class Answer(Base, kw_only=True):
    __tablename__ = 'answer'
    
    @dataclass(frozen=True)
    class Id:
        test_id: int
        test_taker_id: int
        question_discriminator: int
    test_id: Mapped[int_pk] = mapped_column(init=False)
    test_taker_id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[Question.Id] = composite(
        test_id,
        mapped_column('question_discriminator', primary_key=True),
        init=False,
    )
    id: Mapped[Id] = composite(test_id, test_taker_id, 'question_discriminator', init=False)
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'test_taker_id'],
            refcolumns=get_id_columns(TestAttempt),
            ondelete='CASCADE',
        ),
        ForeignKeyConstraint(
            columns=['test_id', 'question_discriminator'],
            refcolumns=get_id_columns(Question),
            ondelete='CASCADE',
        ),
    )
    question: Mapped[Question] = relationship(back_populates='answer_attempts')
    mcq_answer: Mapped[Optional['MCQAnswer']] = relationship(cascade='all, delete-orphan', default=None)
    text_field_answer: Mapped[Optional['TextFieldAnswer']] = relationship(cascade='all, delete-orphan', default=None)
    attachment_answer: Mapped[Optional['AttachmentAnswer']] = relationship(cascade='all, delete-orphan', default=None)
    marks_obtained: Mapped[None | int] = mapped_column(default=None)
    is_bookmarked: Mapped[bool] = mapped_column(default=False)

class MCQAnswer(Base):
    __tablename__ = 'mcq_answer'

    test_id: Mapped[int_pk] = mapped_column(init=False)
    test_taker_id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[Question.Id] = composite(
        test_id,
        mapped_column('question_discriminator', primary_key=True),
        init=False,
    )
    chosen_option_discriminator: Mapped[Optional[int]] = mapped_column(init=False)
    chosen_option: Mapped[Optional[MultipleChoiceQuestion.Option]] = relationship(default=None, overlaps='mcq_answer')
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'test_taker_id', 'question_discriminator'],
            refcolumns=get_id_columns(Answer),
            ondelete='CASCADE',
        ),
        ForeignKeyConstraint(
            columns=['test_id', 'question_discriminator'],
            refcolumns=get_id_columns(MultipleChoiceQuestion),
        ),
        ForeignKeyConstraint(
            columns=['test_id', 'question_discriminator', 'chosen_option_discriminator'],
            refcolumns=get_id_columns(MultipleChoiceQuestion.Option),
        ),
    )

class TextFieldAnswer(Base):
    __tablename__ = 'text_field_answer'

    test_id: Mapped[int_pk] = mapped_column(init=False)
    test_taker_id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[Question.Id] = composite(
        test_id,
        mapped_column('question_discriminator', primary_key=True),
        init=False,
    )
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'test_taker_id', 'question_discriminator'],
            refcolumns=get_id_columns(Answer),
            ondelete='CASCADE',
        ),
        ForeignKeyConstraint(
            columns=['test_id', 'question_discriminator'],
            refcolumns=get_id_columns(TextFieldQuestion),
        ),
    )
    answer_text: Mapped[str] = mapped_column(Text, default='')

class AttachmentAnswer(Base):
    __tablename__ = 'attachment_answer'

    test_id: Mapped[int_pk] = mapped_column(init=False)
    test_taker_id: Mapped[int_pk] = mapped_column(init=False)
    question_id: Mapped[Question.Id] = composite(
        test_id,
        mapped_column('question_discriminator', primary_key=True),
        init=False,
    )
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'test_taker_id', 'question_discriminator'],
            refcolumns=get_id_columns(Answer),
            ondelete='CASCADE',
        ),
        ForeignKeyConstraint(
            columns=['test_id', 'question_discriminator'],
            refcolumns=get_id_columns(AttachmentQuestion),
        ),
    )
    attached_file_url: Mapped[Optional[str]] = mapped_column(default=None)

class GazeData(Base):
    __tablename__ = 'gaze_data'
    
    test_id: Mapped[int_pk] = mapped_column(init=False)
    test_taker_id: Mapped[int_pk] = mapped_column(init=False)
    discriminator: Mapped[int_pk] = mapped_column(autoincrement=True, init=False)
    __table_args__ = (
        ForeignKeyConstraint(
            columns=['test_id', 'test_taker_id'],
            refcolumns=get_id_columns(TestAttempt),
            ondelete='CASCADE',
        ),
    )
    timestamp: Mapped[datetime]
    gaze_extrapolation: Mapped[Point] = composite(mapped_column('x'), mapped_column('y'))