import { Injectable } from '@angular/core';
import { JwtHelperService } from '@auth0/angular-jwt';

import { environment } from '../../environments/environment';

const JWTS_LOCAL_KEY = 'JWTS_LOCAL_KEY';
const JWTS_ACTIVE_INDEX_KEY = 'JWTS_ACTIVE_INDEX_KEY';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  domain = environment.auth0.domain;            // NEW
  audience = environment.auth0.audience;
  clientId = environment.auth0.clientId;
  redirectUri = environment.auth0.redirectUri;  // NEW

  token: string;
  payload: any;

  constructor() { }

  build_login_link(callbackPath = '') {
    let link = 'https://';
    link += this.domain + '/authorize?';  // UPDATED
    link += 'audience=' + this.audience + '&';
    link += 'response_type=token&';
    link += 'client_id=' + this.clientId + '&';
    link += 'redirect_uri=' + this.redirectUri + callbackPath + '&';
    link += 'prompt=login';
    return link;
  }

  check_token_fragment() {
    const fragment = window.location.hash.substr(1).split('&')[0].split('=');
    if (fragment[0] === 'access_token') {
      this.token = fragment[1];
      this.set_jwt();
    }
  }

  set_jwt() {
    localStorage.setItem(JWTS_LOCAL_KEY, this.token);
    if (this.token) {
      this.decodeJWT(this.token);
    }
  }

  load_jwts() {
    this.token = localStorage.getItem(JWTS_LOCAL_KEY) || null;
    if (this.token) {
      this.decodeJWT(this.token);
    }
  }

  activeJWT() {
    return this.token;
  }

  decodeJWT(token: string) {
    const jwtservice = new JwtHelperService();
    this.payload = jwtservice.decodeToken(token);
    return this.payload;
  }

  logout() {
    this.token = '';
    this.payload = null;
    this.set_jwt();
  }

  can(permission: string) {
    return this.payload &&
           this.payload.permissions &&
           this.payload.permissions.length &&
           this.payload.permissions.indexOf(permission) >= 0;
  }
}
