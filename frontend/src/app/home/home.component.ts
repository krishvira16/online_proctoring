import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [ReactiveFormsModule, MatButtonToggleModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  private router = inject(Router)

  roleSelectionForm = new FormGroup({
    role: new FormControl()
  })

  navigateToRolePage() {
    this.router.navigate([this.roleSelectionForm.value.role])
  }
}
