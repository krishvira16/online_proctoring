export interface TestDetails {
  id: number;
  title: string
  description: string
  startTime: Date
  endTime: Date
  guidelines: string
  questions: QuestionDetails[]
}

export interface QuestionDetails {
  discriminator: number;
  question_text: string;
  max_marks: number;
  multiple_choice_question?: MultipleChoiceQuestionDetails;
  text_field_question?: TextFieldQuestionDetails;
  attachment_question?: AttachmentQuestionDetails;
}

export interface MultipleChoiceQuestionDetails {
  options: OptionDetails[];
  correct_option_discriminator: number;
}

export interface OptionDetails {
  discriminator: number;
  option_text: string;
}

export interface TextFieldQuestionDetails {}

export interface AttachmentQuestionDetails {}
