import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { TestDetails } from '../test/test-details.data';
import { DatePipe } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-test-card',
  imports: [MatCardModule, DatePipe, MatButtonModule, RouterLink],
  templateUrl: './test-card.component.html',
  styleUrl: './test-card.component.css',
})
export class TestCardComponent {
  @Input({ required: true }) test!: TestDetails;
}
