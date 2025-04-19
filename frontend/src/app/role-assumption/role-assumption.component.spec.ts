import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoleAssumptionComponent } from './role-assumption.component';

describe('RoleAssumptionComponent', () => {
  let component: RoleAssumptionComponent;
  let fixture: ComponentFixture<RoleAssumptionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoleAssumptionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoleAssumptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
