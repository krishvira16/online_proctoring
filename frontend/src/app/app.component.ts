import { Component, effect, inject, ResourceStatus } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatMenuModule } from '@angular/material/menu';
import { RouterLink, RouterOutlet } from '@angular/router';
import { UserService } from './user/user.service';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { TestService } from './test/test.service';
import { ErrorReportingService } from './error-reporting/error-reporting.service';

@Component({
  selector: 'app-root',
  imports: [
    RouterLink,
    MatToolbarModule,
    MatButtonModule,
    MatMenuModule,
    RouterOutlet,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  private userService = inject(UserService);
  userResource = this.userService.userResource;
  ResourceStatus = ResourceStatus;
  private testService = inject(TestService);
  private errorReportingService = inject(ErrorReportingService)
  loggingOut = false;
  http = inject(HttpClient);

  notLoggedIn() {
    if (!(this.userResource.error() instanceof HttpErrorResponse)) return false;
    return (
      this.userResource.status() === ResourceStatus.Error &&
      (this.userResource.error() as HttpErrorResponse).status === 401
    );
  }

  logOut() {
    this.loggingOut = true;
    this.http.post<void>('/api/user/authentication/logout', undefined).subscribe({
      next: () => {
        this.loggingOut = false;
        this.userService.userResource.reload();
        this.testService.createdTestsResource.reload();
      },
      error: (err) => {
        this.errorReportingService.reportError(err);
      }
    })
  }

  errorAlertEffect = effect(() => {
    if (
      this.userResource.status() === ResourceStatus.Error &&
      !this.notLoggedIn()
    ) {
      const e: any = this.userResource.error();
      alert(`User loading failed with error: ${e.name}("${e.message}")`);
    }
  });
}
