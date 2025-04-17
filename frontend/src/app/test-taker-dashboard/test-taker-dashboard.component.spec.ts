import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TestTakerDashboardComponent } from './test-taker-dashboard.component';

describe('TestTakerDashboardComponent', () => {
  let component: TestTakerDashboardComponent;
  let fixture: ComponentFixture<TestTakerDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestTakerDashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TestTakerDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
