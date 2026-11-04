import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';

/** Pantalla a la que lleva el link del mail de verificación (/verificar-email?token=...). */
@Component({
  selector: 'app-verificar-email',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './verificar-email.html',
  // Usa los mismos estilos que el login.
  styleUrl: '../login/login.css'
})
export class VerificarEmail implements OnInit {
  estado: 'verificando' | 'ok' | 'error' = 'verificando';
  mensaje = '';

  constructor(
    private route: ActivatedRoute,
    private authService: AuthService,
    private changeDetector: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (!token) {
      this.estado = 'error';
      this.mensaje = 'El link no es válido.';
      return;
    }
    this.authService.verificarEmail(token).subscribe({
      next: response => {
        this.estado = 'ok';
        this.mensaje = response?.data || '¡Email verificado! Ya podés iniciar sesión.';
        this.changeDetector.detectChanges();
      },
      error: error => {
        const mensaje = error?.error?.data;
        this.estado = 'error';
        this.mensaje = typeof mensaje === 'string' ? mensaje : 'No se pudo verificar el email. Revisá la conexión con el servidor.';
        this.changeDetector.detectChanges();
      }
    });
  }
}
