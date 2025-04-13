import { TestBed } from '@angular/core/testing';

import { BACKEND_API_BASE_URL } from './backend-api-base-url.service';

describe('BACKEND_API_BASE_URL', () => {
  let service: string;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BACKEND_API_BASE_URL);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
