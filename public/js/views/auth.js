import { API } from '../services/api.js';
import { setSession } from '../services/session.js';
import { COUNTRY_CODES } from '../shared/constants.js';
import { formData, go, root, toast } from '../shared/dom.js';
import { esc } from '../shared/format.js';
import { logoMark } from '../components/ui.js';

function countryCodeSelect(current = '+91') {
  return `<select name="countryCode" aria-label="Country code">${COUNTRY_CODES
    .map(({ code, flag }) => `<option value="${code}" ${code === current ? 'selected' : ''}>${flag} ${code}</option>`)
    .join('')}</select>`;
}

function fullPhone(countryCode, phone) {
  const digits = String(phone || '').replace(/[^\d]/g, '');
  return `${countryCode || '+91'}${digits}`;
}

function googleBtn(type) {
  return `
    <a class="btn-google" href="/api/auth/google/login?account_type=${type}">
      ${gIcon()} Continue with Google</a>`;
}

const gIcon = () =>
  `<svg viewBox="0 0 24 24"><path fill="#4285F4" d="M22 12c0-.7-.1-1.4-.2-2H12v4h5.6a4.8 4.8 0 0 1-2 3.1v2.6h3.2C20.7 18 22 15.3 22 12z"/><path fill="#34A853" d="M12 22c2.7 0 5-1 6.6-2.4l-3.2-2.5c-.9.6-2 1-3.4 1-2.6 0-4.8-1.7-5.6-4.1H3.1v2.6A10 10 0 0 0 12 22z"/><path fill="#FBBC05" d="M6.4 14C6.2 13.4 6 12.7 6 12s.2-1.4.4-2V7.4H3.1A10 10 0 0 0 2 12c0 1.6.4 3.1 1.1 4.6L6.4 14z"/><path fill="#EA4335" d="M12 6c1.5 0 2.8.5 3.8 1.5l2.8-2.8A10 10 0 0 0 3.1 7.4L6.4 10c.8-2.4 3-4 5.6-4z"/></svg>`;

export function renderLogin() {
  let type = '';
  let channel = 'email';
  let sent = false;
  let value = '';
  function paint() {
    root.innerHTML = `
      <div class="auth-wrap"><div class="auth-card">
        ${logoMark()}
        <h1>Welcome back</h1>
        <p class="sub">Choose your workspace, then log in with a one-time code or Google.</p>
        <div class="role-toggle" aria-label="Choose account type">
          <button data-t="creator" class="${type === 'creator' ? 'active' : ''}">I'm a creator</button>
          <button data-t="brand" class="${type === 'brand' ? 'active' : ''}">I'm a brand</button>
        </div>
        ${
          type
            ? `<div class="seg">
                <button data-ch="email" class="${channel === 'email' ? 'active' : ''}">Email</button>
                <button data-ch="phone" class="${channel === 'phone' ? 'active' : ''}">Phone</button>
              </div>
              <form id="otpForm">
                <div class="field">
                  <label>${channel === 'email' ? 'Email address' : 'Phone number'}</label>
                  ${
                    channel === 'email'
                      ? `<input name="value" value="${esc(value)}" placeholder="you@example.com" ${sent ? 'readonly' : ''} required />`
                      : `<div class="phone-row">${countryCodeSelect('+91')}<input name="value" value="${esc(value)}" inputmode="tel" placeholder="98765 43210" ${sent ? 'readonly' : ''} required /></div>`
                  }
                </div>
                ${
                  sent
                    ? `<div class="field"><label>Enter code</label><input name="code" placeholder="6-digit code" required />
                       <div class="hint" id="devhint"></div></div>
                       <button class="btn btn-primary btn-block" type="submit">Verify &amp; log in</button>`
                    : `<button class="btn btn-primary btn-block" type="submit">Send code</button>`
                }
              </form>
              <div class="divider">or</div>
              ${googleBtn(type)}`
            : ''
        }
        <p class="auth-alt">New to linc? <a id="toSignup">Create an account</a></p>
      </div></div>`;
    root.querySelectorAll('[data-t]').forEach((button) => {
      button.onclick = () => {
        type = button.dataset.t;
        sent = false;
        value = '';
        paint();
      };
    });
    root.querySelectorAll('[data-ch]').forEach((button) => {
      button.onclick = () => {
        channel = button.dataset.ch;
        sent = false;
        value = '';
        paint();
      };
    });
    document.getElementById('toSignup').onclick = () => go('#/signup');
    const otpForm = document.getElementById('otpForm');
    if (!otpForm) return;
    otpForm.onsubmit = async (event) => {
      event.preventDefault();
      const data = formData(event.target);
      try {
        if (!sent) {
          const otpValue = channel === 'phone' ? fullPhone(data.countryCode, data.value) : data.value;
          const result = await API.post('/api/auth/otp/request', { channel, value: otpValue, accountType: type });
          value = data.value;
          sent = true;
          paint();
          value = otpValue;
          if (result.devCode) {
            document.getElementById('devhint').innerHTML =
              `Demo mode: any code works. Suggested code: <strong>${result.devCode}</strong>`;
          }
        } else {
          const session = await API.post('/api/auth/otp/verify', { channel, value, code: data.code, accountType: type });
          API.setToken(session.token);
          setSession(session);
          toast('Logged in', 'success');
          go(`#/${session.accountType}`);
        }
      } catch (err) {
        toast(err.detail || 'Something went wrong', 'error');
      }
    };
  }
  paint();
}

export function renderSignup() {
  let type = '';
  function paint() {
    root.innerHTML = `
      <div class="auth-wrap"><div class="auth-card">
        ${logoMark()}
        <h1>Create your account</h1>
        <p class="sub">Join linc as a creator or a brand.</p>
        <div class="role-toggle" aria-label="Choose account type">
          <button data-t="creator" class="${type === 'creator' ? 'active' : ''}">I'm a creator</button>
          <button data-t="brand" class="${type === 'brand' ? 'active' : ''}">I'm a brand</button>
        </div>
        ${
          type
            ? `<form id="suForm">
                <div class="field"><label>${type === 'creator' ? 'Name' : 'Brand name'}</label><input name="name" required /></div>
                <div class="field-row">
                  <div class="field"><label>Email</label><input name="email" type="email" required /></div>
                  <div class="field"><label>Phone</label><div class="phone-row">${countryCodeSelect('+91')}<input name="phone" inputmode="tel" placeholder="98765 43210" required /></div></div>
                </div>
                ${
                  type === 'creator'
                    ? `<div class="field"><label>Niche <span class="optional-label">optional</span></label><input name="niche" placeholder="Beauty, Food, Tech..." /></div>`
                    : `<div class="field"><label>Category <span class="optional-label">optional</span></label><input name="category" placeholder="D2C, SaaS..." /></div>`
                }
                <button class="btn btn-primary btn-block" type="submit">Create account</button>
              </form>
              <div class="divider">or</div>
              ${googleBtn(type)}`
            : ''
        }
        <p class="auth-alt">Already have an account? <a id="toLogin">Log in</a></p>
      </div></div>`;
    root.querySelectorAll('[data-t]').forEach((button) => {
      button.onclick = () => {
        type = button.dataset.t;
        paint();
      };
    });
    document.getElementById('toLogin').onclick = () => go('#/login');
    const signupForm = document.getElementById('suForm');
    if (!signupForm) return;
    signupForm.onsubmit = async (event) => {
      event.preventDefault();
      const data = formData(event.target);
      try {
        data.phone = fullPhone(data.countryCode, data.phone);
        delete data.countryCode;
        await API.post(type === 'creator' ? '/api/creators' : '/api/brands', data);
        const result = await API.post('/api/auth/otp/request', { channel: 'email', value: data.email, accountType: type });
        toast('Account created — check your code to log in', 'success');
        renderVerifyAfterSignup(data.email, type, result.devCode);
      } catch (err) {
        toast(err.detail || 'Could not create account', 'error');
      }
    };
  }
  paint();
}

function renderVerifyAfterSignup(email, type, devCode) {
  root.innerHTML = `
    <div class="auth-wrap"><div class="auth-card">
      ${logoMark()}
      <h1>Verify your email</h1>
      <p class="sub">We sent a code to ${esc(email)}.</p>
      <form id="vForm">
        <div class="field"><label>Enter code</label><input name="code" placeholder="6-digit code" required />
        <div class="hint">Demo mode: any code works.${devCode ? ` Suggested code: <strong>${devCode}</strong>` : ''}</div></div>
        <button class="btn btn-primary btn-block" type="submit">Verify &amp; continue</button>
      </form>
    </div></div>`;
  document.getElementById('vForm').onsubmit = async (event) => {
    event.preventDefault();
    try {
      const session = await API.post('/api/auth/otp/verify', {
        channel: 'email',
        value: email,
        code: formData(event.target).code,
        accountType: type,
      });
      API.setToken(session.token);
      setSession(session);
      go(`#/${session.accountType}`);
    } catch (err) {
      toast(err.detail || 'Invalid code', 'error');
    }
  };
}

