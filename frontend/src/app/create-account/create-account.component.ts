import { HttpClient } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import {
  ReactiveFormsModule,
  FormGroup,
  FormControl,
  Validators,
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { UserService } from '../user/user.service';
import { ErrorReportingService } from '../error-reporting/error-reporting.service';
import { TestService } from '../test/test.service';

@Component({
  selector: 'app-create-account',
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatButtonModule,
    MatDividerModule,
    RouterLink,
  ],
  templateUrl: './create-account.component.html',
  styleUrl: './create-account.component.css',
})
export class CreateAccountComponent {
  createAccountFormGroup = new FormGroup({
    username: new FormControl<string>('', [Validators.required]),
    fullName: new FormControl<string>('', [Validators.required]),
    email: new FormControl<string>('', [Validators.required, Validators.email]),
    password: new FormControl<string>('', [Validators.required]),
    remember: new FormControl<boolean>(false),
  });

  private http = inject(HttpClient);
  private router = inject(Router);
  private userService = inject(UserService);
  private testService = inject(TestService);
  private errorReportingService = inject(ErrorReportingService);

  creating = false;
  loggingIn = false;
  errorOccurred = false;
  errorMessage = '';

  createAccount() {
    if (this.createAccountFormGroup.invalid) return;
    this.creating = true;
    this.errorOccurred = false;
    const createAccount$ = this.http.post<void>(
      '/api/user/create_account',
      {
        username: this.createAccountFormGroup.value.username,
        fullName: this.createAccountFormGroup.value.fullName,
        email: this.createAccountFormGroup.value.email,
        password: this.createAccountFormGroup.value.password,
      }
    );
    createAccount$.subscribe({
      next: () => {
        this.creating = false;
        this.loggingIn = true
        const attemptLogin$ = this.http.post<void>(
          '/api/user/authentication/login',
          {
            username: this.createAccountFormGroup.value.username,
            password: this.createAccountFormGroup.value.password,
          },
          {
            params: {
              remember: this.createAccountFormGroup.value.remember as boolean,
            },
          }
        );
        attemptLogin$.subscribe({
          next: () => {
            this.userService.userResource.reload();
            this.testService.createdTestsResource.reload();
            const continuePath = history.state.continue ?? '/';
            this.router.navigate([continuePath]);
          },
          error: (err) => {this.errorReportingService.reportError(err)}
        });
      },
      error: (err) => {
        if (err.status === 422) {
          this.creating = false;
          this.errorOccurred = true;
          this.errorMessage = err.error
        } else {
          this.errorReportingService.reportError(err)
        }
      },
    });
  }
}
