import { HttpClient } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';
import { TestService } from '../test/test.service';
import { ErrorReportingService } from '../error-reporting/error-reporting.service';

@Component({
  selector: 'app-role-assumption',
  imports: [MatButtonModule],
  templateUrl: './role-assumption.component.html',
  styleUrl: './role-assumption.component.css',
})
export abstract class RoleAssumptionComponent {
  role!: { displayName: string; path: string };
  http = inject(HttpClient);
  router = inject(Router);
  errorReportingService = inject(ErrorReportingService);
  registering = false;

  assumeRole() {
    this.registering = true;
    this.http
      .post<void>(`/api/${this.role.path}/assume_role`, undefined)
      .subscribe({
        next: () => {
          this.reloadState();
          const continuePath = history.state.continue ?? '/';
          this.router.navigate([continuePath]);
        },
        error: (err) => {
          this.errorReportingService.reportError(err)
        },
      });
  }

  abstract reloadState(): void;
}

@Component({
  selector: 'app-test-setter-role-assumption',
  imports: [MatButtonModule],
  templateUrl: './role-assumption.component.html',
  styleUrl: './role-assumption.component.css',
})
export class TestSetterRoleAssumptionComponent extends RoleAssumptionComponent {
  override role = {displayName: 'test setter', path: '/test_setter'}
  testService = inject(TestService);

  override reloadState(): void {
    this.testService.createdTestsResource.reload();
  }
}

// @Component({
//   selector: 'app-test-taker-role-assumption',
//   imports: [MatButtonModule],
//   templateUrl: './role-assumption.component.html',
//   styleUrl: './role-assumption.component.css',
// })
// export class TestTakerRoleAssumptionComponent extends RoleAssumptionComponent {
//   override role = { displayName: 'test taker', path: '/test_taker' };
// }

// @Component({
//   selector: 'app-invigilator-role-assumption',
//   imports: [MatButtonModule],
//   templateUrl: './role-assumption.component.html',
//   styleUrl: './role-assumption.component.css',
// })
// export class InvigilatorRoleAssumptionComponent extends RoleAssumptionComponent {
//   override role = { displayName: 'invigilator', path: '/invigilator' };
// }
