import { Component, effect, inject, Input } from '@angular/core';
import { TestService } from './test.service';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import {
  FormArray,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatTimepickerModule } from '@angular/material/timepicker';
import { MatButtonModule } from '@angular/material/button';
import { MatRadioModule } from '@angular/material/radio';
import { HttpClient } from '@angular/common/http';
import { ErrorReportingService } from '../error-reporting/error-reporting.service';
import { ActivatedRoute } from '@angular/router';

interface TestForm {
  id: FormControl<number>;
  title: FormControl<string>;
  description: FormControl<string>;
  startTime: FormControl<Date>;
  endTime: FormControl<Date>;
  guidelines: FormControl<string>;
  questions: FormArray<FormGroup<QuestionForm>>;
}

interface QuestionForm {
  discriminator: FormControl<number>;
  questionText: FormControl<string>;
  maxMarks: FormControl<number>;
  multipleChoiceQuestion?: FormGroup<MultipleChoiceQuestionForm>;
  textFieldQuestion?: FormGroup<TextFieldQuestionForm>;
  attachmentQuestion?: FormGroup<AttachmentQuestionForm>;
}

interface MultipleChoiceQuestionForm {
  options: FormArray<FormGroup<OptionForm>>;
  correctOptionDiscriminator: FormControl<number>;
}

interface OptionForm {
  discriminator: FormControl<number>;
  optionText: FormControl<string>;
}

interface TextFieldQuestionForm {}

interface AttachmentQuestionForm {}

class NegativeCounter {
  private counter = 0;
  get nextCountValue() {
    return --this.counter;
  }
}

@Component({
  selector: 'app-test',
  imports: [
    MatTabsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatTimepickerModule,
    MatButtonModule,
    MatRadioModule,
  ],
  templateUrl: './test.component.html',
  styleUrl: './test.component.css',
})
export class TestComponent {
  counter = new NegativeCounter();

  testService = inject(TestService);
  route = inject(ActivatedRoute);
  testIdStr = this.route.snapshot.paramMap.get('testIdStr');
  testId = this.testIdStr ? parseInt(this.testIdStr) : null;
  test = this.testId
    ? this.testService.createdTestsResource
        .value()
        ?.find((test) => test.id === this.testId)
    : null;
  testForm: FormGroup<TestForm> = this.createTestForm();

  testLoadingEffect = effect(() => {
    if (this.testId) {
      const test = this.testService.createdTestsResource
        .value()
        ?.find((test) => test.id === this.testId);
      if (test) {
        // TODO: this might not work, so create an effect.
        test.questions.forEach((question) => {
          const questionForm = this.createQuestionForm();
          if (question.multipleChoiceQuestion) {
            const multipleChoiceQuestionForm =
              this.createMultipleChoiceQuestionForm();
            question.multipleChoiceQuestion.options.forEach((option) => {
              multipleChoiceQuestionForm.controls.options.push(
                this.createOptionForm()
              );
            });
            questionForm.controls.multipleChoiceQuestion =
              multipleChoiceQuestionForm;
          }
          if (question.textFieldQuestion) {
            questionForm.controls.textFieldQuestion =
              this.createTextFieldQuestionForm();
          }
          if (question.attachmentQuestion) {
            questionForm.controls.attachmentQuestion =
              this.createAttachmentQuestionForm();
          }
          this.testForm.controls.questions.push(questionForm);
        });
        this.testForm.setValue(test);
      }
    }
  });

  // constructor() {
  //   this.testForm = this.createTestForm();
  //   if (this.test) {
  //     // TODO: this might not work, so create an effect.
  //     this.test.questions.forEach((question) => {
  //       const questionForm = this.createQuestionForm();
  //       if (question.multipleChoiceQuestion) {
  //         const multipleChoiceQuestionForm =
  //           this.createMultipleChoiceQuestionForm();
  //         question.multipleChoiceQuestion.options.forEach((option) => {
  //           multipleChoiceQuestionForm.controls.options.push(
  //             this.createOptionForm()
  //           );
  //         });
  //         questionForm.controls.multipleChoiceQuestion =
  //           multipleChoiceQuestionForm;
  //       }
  //       if (question.textFieldQuestion) {
  //         questionForm.controls.textFieldQuestion =
  //           this.createTextFieldQuestionForm();
  //       }
  //       if (question.attachmentQuestion) {
  //         questionForm.controls.attachmentQuestion =
  //           this.createAttachmentQuestionForm();
  //       }
  //       this.testForm.controls.questions.push(questionForm);
  //     });
  //     this.testForm.setValue(this.test);
  //   }
  // }

  createTestForm() {
    return new FormGroup<TestForm>({
      id: new FormControl<number>(this.counter.nextCountValue, {
        nonNullable: true,
        validators: [Validators.required],
      }),
      title: new FormControl<string>('', {
        nonNullable: true,
        validators: [Validators.required],
      }),
      description: new FormControl<string>('', {
        nonNullable: true,
        validators: [Validators.required],
      }),
      startTime: new FormControl<Date>(undefined!, {
        nonNullable: true,
        validators: [Validators.required],
      }),
      endTime: new FormControl<Date>(undefined!, {
        nonNullable: true,
        validators: [Validators.required],
      }),
      guidelines: new FormControl<string>('', {
        nonNullable: true,
        validators: [Validators.required],
      }),
      questions: new FormArray<FormGroup<QuestionForm>>([]),
    });
  }

  createQuestionForm() {
    return new FormGroup<QuestionForm>({
      discriminator: new FormControl<number>(this.counter.nextCountValue, {
        nonNullable: true,
        validators: [Validators.required],
      }),
      questionText: new FormControl<string>('', {
        nonNullable: true,
        validators: [Validators.required],
      }),
      maxMarks: new FormControl<number>(undefined!, {
        nonNullable: true,
        validators: [Validators.required],
      }),
    });
  }

  createMultipleChoiceQuestionForm() {
    return new FormGroup<MultipleChoiceQuestionForm>({
      options: new FormArray<FormGroup<OptionForm>>([]),
      correctOptionDiscriminator: new FormControl<number>(undefined!, {
        nonNullable: true,
        validators: [Validators.required],
      }),
    });
  }

  createOptionForm() {
    return new FormGroup<OptionForm>({
      discriminator: new FormControl<number>(this.counter.nextCountValue, {
        nonNullable: true,
        validators: [Validators.required],
      }),
      optionText: new FormControl<string>('', {
        nonNullable: true,
        validators: [Validators.required],
      }),
    });
  }

  createTextFieldQuestionForm() {
    return new FormGroup<TextFieldQuestionForm>({});
  }

  createAttachmentQuestionForm() {
    return new FormGroup<AttachmentQuestionForm>({});
  }

  http = inject(HttpClient);
  errorReportingService = inject(ErrorReportingService);
  saving = false;
  display_error_message = false;

  saveTest() {
    console.log(this.testForm.errors);

    if (this.testForm.invalid) {
      this.display_error_message = true;
      return;
    }
    this.display_error_message = false;
    this.saving = true;
    if (this.testForm.controls.id.value < 0) {
      this.http
        .post<void>('/api/test_setter/create_test', this.testForm.value)
        .subscribe({
          next: () => {
            this.saving = false;
          },
          error: (err) => {
            this.errorReportingService.reportError(err);
          },
        });
    }
  }
}
