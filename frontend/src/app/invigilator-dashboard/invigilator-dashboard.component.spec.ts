import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvigilatorDashboardComponent } from './invigilator-dashboard.component';

describe('InvigilatorDashboardComponent', () => {
  let component: InvigilatorDashboardComponent;
  let fixture: ComponentFixture<InvigilatorDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InvigilatorDashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InvigilatorDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
