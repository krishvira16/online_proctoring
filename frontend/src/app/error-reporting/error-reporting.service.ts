import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ErrorReportingService {
  reportError(err: Error) {
    alert(`An error occurred: ${err.name}("${err.message}")`)
  }
}
