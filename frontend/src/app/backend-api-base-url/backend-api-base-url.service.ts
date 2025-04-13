import { InjectionToken } from '@angular/core';

import { BACKEND_API_BASE_URL_VALUE } from './backend-api-base-url-value';

export const BACKEND_API_BASE_URL = new InjectionToken<string>(
  'The base URL for the backend API',
  {
    providedIn: 'root',
    factory: () => BACKEND_API_BASE_URL_VALUE,
  }
);
