import { Component, effect, inject, ResourceStatus } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatMenuModule } from '@angular/material/menu';
import { RouterLink, RouterOutlet } from '@angular/router';
import { UserService } from './user/user.service';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-root',
  imports: [RouterLink, MatToolbarModule, MatMenuModule, RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  private userService = inject(UserService);
  userResource = this.userService.userResource
  ResourceStatus = ResourceStatus

  notLoggedIn() {
    if (!(this.userResource.error() instanceof HttpErrorResponse)) return false;
    return (
      this.userResource.status() === ResourceStatus.Error &&
      (this.userResource.error() as HttpErrorResponse).status === 401
    );
  }

  errorAlertEffect = effect(() => {
    const e: any = this.userResource.error();
    if (e) {
      alert(`User loading failed with error: ${e.name}("${e.message}")`)
    }
  });
}
