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
  questionText: string;
  maxMarks: number;
  multipleChoiceQuestion?: MultipleChoiceQuestionDetails;
  textFieldQuestion?: TextFieldQuestionDetails;
  attachmentQuestion?: AttachmentQuestionDetails;
}

export interface MultipleChoiceQuestionDetails {
  options: OptionDetails[];
  correctOptionDiscriminator: number;
}

export interface OptionDetails {
  discriminator: number;
  optionText: string;
}

export interface TextFieldQuestionDetails {}

export interface AttachmentQuestionDetails {}
