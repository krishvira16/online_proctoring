import { Component, effect, inject } from '@angular/core';
import { TestService } from '../test/test.service';
import { TestCardComponent } from '../test-card/test-card.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-test-setter-dashboard',
  imports: [TestCardComponent],
  templateUrl: './test-setter-dashboard.component.html',
  styleUrl: './test-setter-dashboard.component.css',
})
export class TestSetterDashboardComponent {
  private testService = inject(TestService);
  createdTestsResource = this.testService.createdTestsResource;

  router = inject(Router)

  authenticationErrorEffect = effect(() => {
    const e: any = this.createdTestsResource.error();
    if (e) {
      if (e.status === 401) {
        this.router.navigate(['/login'], {state: {continue: '/test_setter'}});
      } else if (e.status === 403) {
        // TODO: handle role assumption
      }
    }
  });
}
