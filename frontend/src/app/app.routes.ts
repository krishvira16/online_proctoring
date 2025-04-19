import { Routes, UrlSegment } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { TestSetterDashboardComponent } from './test-setter-dashboard/test-setter-dashboard.component';
import { TestTakerDashboardComponent } from './test-taker-dashboard/test-taker-dashboard.component';
import { InvigilatorDashboardComponent } from './invigilator-dashboard/invigilator-dashboard.component';
import { LoginComponent } from './login/login.component';
import { CreateAccountComponent } from './create-account/create-account.component';
import { TestSetterRoleAssumptionComponent } from './role-assumption/role-assumption.component';
import { TestComponent } from './test/test.component';

export const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
  },
  {
    path: 'create_account',
    component: CreateAccountComponent,
  },
  {
    path: 'login',
    component: LoginComponent,
  },
  {
    path: 'test_setter/assume_role',
    component: TestSetterRoleAssumptionComponent,
  },
  {
    path: 'test_setter',
    component: TestSetterDashboardComponent,
  },
  {
    path: 'test_setter/test',
    component: TestComponent,
  },
  {
    path: 'test_setter/test/:testIdStr',
    component: TestComponent,
  },
  {
    matcher: (url) => {
      if (
        url.length === 2 &&
        url[0].path === 'test_setter' &&
        url[1].path === 'test'
        // &&
        // url[2].path.match(/^\d+$/gm)
      ) {
        return {
          consumed: url,
          // posParams: { testIdStr: new UrlSegment(url[2].path, {}) },
        };
      }
      return null;
    },
    component: TestComponent,
  },
  {
    path: 'test_taker',
    component: TestTakerDashboardComponent,
  },
  {
    path: 'invigilator',
    component: InvigilatorDashboardComponent,
  },
];
