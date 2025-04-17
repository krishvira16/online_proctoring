import { inject, Injectable, resource } from '@angular/core';
import { BACKEND_API_BASE_URL } from '../backend-api-base-url/backend-api-base-url.service';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom, takeUntil, fromEvent } from 'rxjs';
import { TestDetails } from './test-details.data';

@Injectable({
  providedIn: 'root',
})
export class TestService {
  private backend_api_base_url = inject(BACKEND_API_BASE_URL);
  private http = inject(HttpClient);

  createdTestsResource = resource({
    loader: ({request, previous, abortSignal}) => {
      return firstValueFrom(
        this.http
          .get<TestDetails[]>(`${this.backend_api_base_url}/test_setter/tests`)
          .pipe(takeUntil(fromEvent(abortSignal, 'abort')))
      );
    }
  })
}
