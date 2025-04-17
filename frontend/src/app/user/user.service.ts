import { inject, Injectable, resource } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserDetails } from './user-details.data';
import { firstValueFrom, fromEvent, takeUntil } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);

  userResource = resource({
    loader: ({ request, previous, abortSignal }) => {
      return firstValueFrom(
        this.http
          .get<UserDetails>('/api/user/details')
          .pipe(takeUntil(fromEvent(abortSignal, 'abort')))
      );
    },
  });
}
