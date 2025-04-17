import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { TestSetterDashboardComponent } from './test-setter-dashboard/test-setter-dashboard.component';
import { TestTakerDashboardComponent } from './test-taker-dashboard/test-taker-dashboard.component';
import { InvigilatorDashboardComponent } from './invigilator-dashboard/invigilator-dashboard.component';
import { LoginComponent } from './login/login.component';
import { CreateAccountComponent } from './create-account/create-account.component';

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
    path: 'test_setter',
    component: TestSetterDashboardComponent,
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
