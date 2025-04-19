import { Component, effect, inject, ResourceStatus } from '@angular/core';
import { TestService } from '../test/test.service';
import { TestCardComponent } from '../test-card/test-card.component';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-test-setter-dashboard',
  imports: [MatButtonModule, RouterLink, TestCardComponent],
  templateUrl: './test-setter-dashboard.component.html',
  styleUrl: './test-setter-dashboard.component.css',
})
export class TestSetterDashboardComponent {
  private testService = inject(TestService);
  createdTestsResource = this.testService.createdTestsResource;

  router = inject(Router);

  authenticationErrorEffect = effect(() => {
    if (this.createdTestsResource.status() === ResourceStatus.Error) {
      const e: any = this.createdTestsResource.error();
      if (e.status === 401) {
        this.router.navigate(['/login'], {
          state: { continue: '/test_setter' },
        });
      } else if (e.status === 403) {
        this.router.navigate(['/test_setter/assume_role'], {
          state: { continue: '/test_setter' },
        });
      }
    }
  });
}
