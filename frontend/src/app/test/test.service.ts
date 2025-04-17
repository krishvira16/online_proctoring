import { inject, Injectable, resource } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom, takeUntil, fromEvent } from 'rxjs';
import { TestDetails } from './test-details.data';

@Injectable({
  providedIn: 'root',
})
export class TestService {
  private http = inject(HttpClient);

  createdTestsResource = resource({
    loader: ({ request, previous, abortSignal }) => {
      return firstValueFrom(
        this.http
          .get<TestDetails[]>('/api/test_setter/tests')
          .pipe(takeUntil(fromEvent(abortSignal, 'abort')))
      );
    },
  });
}
