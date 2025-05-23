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
  selector: 'app-login',
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatButtonModule,
    MatDividerModule,
    RouterLink,
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  loginFormGroup = new FormGroup({
    username: new FormControl<string>('', [Validators.required]),
    password: new FormControl<string>('', [Validators.required]),
    remember: new FormControl<boolean>(false),
  });

  private http = inject(HttpClient);
  private router = inject(Router);
  private userService = inject(UserService);
  private testService = inject(TestService)
  private errorReportingService = inject(ErrorReportingService);

  verifying = false;
  invalid_credentials = false;

  attemptLogin() {
    if (this.loginFormGroup.invalid) return;
    this.verifying = true;
    this.invalid_credentials = false;
    const attemptLogin$ = this.http.post<void>(
      '/api/user/authentication/login',
      {
        username: this.loginFormGroup.value.username,
        password: this.loginFormGroup.value.password,
      },
      {
        params: {
          remember: this.loginFormGroup.value.remember as boolean,
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
      error: (err) => {
        if (err.status === 401) {
          this.verifying = false;
          this.invalid_credentials = true;
        } else {
          this.errorReportingService.reportError(err)
        }
      },
    });
  }
}
