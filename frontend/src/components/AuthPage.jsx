import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { Icon } from './Icons'
import { useSettings } from '../settings'

export default function AuthPage({ mode, onAuthenticated }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const isLogin = mode === 'login'
  const { t } = useSettings()

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await api(`/api/auth/${mode}`, { method: 'POST', body: form })
      onAuthenticated(data.user)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return <main className="auth-page">
    <section className="auth-showcase">
      <div className="auth-showcase-content">
        <span className="hero-tag"><Icon name="sparkles" /> {t('authTag')}</span>
        <h1>{t('authTitle1')}<br />{t('authTitle2')}</h1>
        <p>{t('authText')}</p>
      </div>
    </section>
    <section className="auth-panel">
      <div className="auth-card">
        <span className="eyebrow">{t('personalSpace')}</span>
        <h2>{isLogin ? t('welcomeBack') : t('createAccount')}</h2>
        <p>{isLogin ? t('loginText') : t('registerText')}</p>
        <form onSubmit={submit}>
          {!isLogin && <label>{t('name')}
            <input name="username" value={form.username} onChange={update} minLength="2" maxLength="40" required autoComplete="name" />
          </label>}
          <label>{t('email')}
            <input name="email" type="email" value={form.email} onChange={update} required autoComplete="email" />
          </label>
          <label>{t('password')}
            <input name="password" type="password" value={form.password} onChange={update} required minLength={isLogin ? 1 : 10} autoComplete={isLogin ? 'current-password' : 'new-password'} />
          </label>
          {!isLogin && <small>{t('passwordHint')}</small>}
          {error && <div className="form-error">{error}</div>}
          <button className="primary-button full" disabled={loading}>{loading ? t('oneMoment') : isLogin ? t('login') : t('createAccount')}</button>
        </form>
        <p className="auth-switch">{isLogin ? t('noAccount') : t('hasAccount')} <Link to={isLogin ? '/register' : '/login'}>{isLogin ? t('createAccountLink') : t('login')}</Link></p>
      </div>
    </section>
  </main>
}
