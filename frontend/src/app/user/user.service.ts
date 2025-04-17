import { inject, Injectable, resource } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserDetails } from './user-details.data';
import { BACKEND_API_BASE_URL } from '../backend-api-base-url/backend-api-base-url.service';
import { firstValueFrom, fromEvent, takeUntil } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserService {
  private backend_api_base_url = inject(BACKEND_API_BASE_URL);
  private http = inject(HttpClient);

  userResource = resource({
    loader: ({ request, previous, abortSignal }) => {
      return firstValueFrom(
        this.http
          .get<UserDetails>(`${this.backend_api_base_url}/user/details`)
          .pipe(takeUntil(fromEvent(abortSignal, 'abort')))
      );
    },
  });
}
