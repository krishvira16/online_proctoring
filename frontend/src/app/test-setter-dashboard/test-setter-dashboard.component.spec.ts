import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TestSetterDashboardComponent } from './test-setter-dashboard.component';

describe('TestSetterDashboardComponent', () => {
  let component: TestSetterDashboardComponent;
  let fixture: ComponentFixture<TestSetterDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestSetterDashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TestSetterDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
