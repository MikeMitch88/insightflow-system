import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({ selector: 'app-login', templateUrl: './login.component.html', styleUrls: ['./login.component.css'] })
export class LoginComponent implements OnInit {
  email = ''; password = ''; rememberEmail = false; showPassword = false; submitted = false; error = ''; info = ''; loading = false;
  constructor(private auth: AuthService, private router: Router) { if (auth.isLoggedIn()) router.navigate(['/dashboard']); }
  ngOnInit(): void { const savedEmail = localStorage.getItem('insightflow.rememberedEmail'); if (savedEmail) { this.email = savedEmail; this.rememberEmail = true; } }
  togglePasswordVisibility(): void { this.showPassword = !this.showPassword; }
  saveRememberedEmail(): void { if (this.rememberEmail && this.email) localStorage.setItem('insightflow.rememberedEmail', this.email); else if (!this.rememberEmail) localStorage.removeItem('insightflow.rememberedEmail'); }
  showPasswordHelp(): void { this.error = ''; this.info = 'Please contact your InsightFlow administrator to reset your password.'; }
  login(form: NgForm): void { this.submitted = true; this.error = ''; this.info = ''; if (form.invalid) return; this.saveRememberedEmail(); this.loading = true; this.auth.login(this.email.trim(), this.password).subscribe({ next: () => this.router.navigate(['/dashboard']), error: (err) => { this.loading = false; this.error = err.error?.detail || 'We could not sign you in. Check your details and try again.'; } }); }
}
