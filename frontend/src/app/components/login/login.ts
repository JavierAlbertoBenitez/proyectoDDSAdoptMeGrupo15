import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  email = '';
  password = '';
  ingresando = false;
  error = '';
  // Mensaje informativo (por ejemplo, despues de registrarse: "te mandamos un mail").
  aviso = '';
  // El back rechazo el login porque falta verificar el email: mostramos "Reenviar mail".
  emailSinVerificar = false;
  reenviando = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private toastr: ToastrService,
    private changeDetector: ChangeDetectorRef
  ) {
    // El registro nos manda aca con ?verificar=<email> despues de crear la cuenta.
    const registrado = this.route.snapshot.queryParamMap.get('verificar');
    if (registrado) {
      this.email = registrado;
      this.emailSinVerificar = true;
      this.aviso = `Te enviamos un mail a ${registrado} para verificar tu cuenta. Abrí el link y después iniciá sesión.`;
    }
  }

  login(): void {
    if (this.ingresando) {
      return;
    }
    this.ingresando = true;
    this.error = '';
    this.aviso = '';
    this.emailSinVerificar = false;
    this.authService.login(this.email.trim(), this.password).subscribe({
      next: () => {
        this.toastr.success('Sesión iniciada.');
        if (this.authService.esModerador()) {
          this.router.navigateByUrl('/moderacion');
          return;
        }
        const requestedUrl = this.route.snapshot.queryParamMap.get('returnUrl');
        const destination = requestedUrl?.startsWith('/') && !requestedUrl.startsWith('//')
          ? requestedUrl
          : '/publicaciones';
        this.router.navigateByUrl(destination);
      },
      error: error => {
        console.error('No se pudo iniciar sesión.', error);
        const message = error?.error?.data;
        this.error = typeof message === 'string' ? message : 'No se pudo iniciar sesión. Revisá tus datos y que el servidor esté activo.';
        if (error?.status === 404) {
          this.toastr.warning(this.error, 'La cuenta no existe');
        } else if (error?.error?.codigo === 'EMAIL_NO_VERIFICADO') {
          this.emailSinVerificar = true;
        } else {
          this.toastr.error(this.error);
        }
        this.ingresando = false;
        // Sin esto el botón se queda en "Ingresando..." hasta que se toque algo.
        this.changeDetector.detectChanges();
      }
    });
  }

  reenviarVerificacion(): void {
    const email = this.email.trim();
    if (!email || this.reenviando) {
      this.error = email ? this.error : 'Escribí tu correo electrónico para reenviarte el mail.';
      return;
    }
    this.reenviando = true;
    this.authService.reenviarVerificacion(email).subscribe({
      next: response => {
        this.reenviando = false;
        this.error = '';
        this.aviso = response?.data || 'Te enviamos un nuevo mail.';
        this.changeDetector.detectChanges();
      },
      error: error => {
        const mensaje = error?.error?.data;
        this.reenviando = false;
        this.toastr.error(typeof mensaje === 'string' ? mensaje : 'No se pudo reenviar el mail.');
        this.changeDetector.detectChanges();
      }
    });
  }
}
