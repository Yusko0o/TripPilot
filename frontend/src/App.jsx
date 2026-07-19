import { useEffect, useState } from 'react'
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './api'
import AirportAutocomplete from './components/AirportAutocomplete'
import AuthPage from './components/AuthPage'
import Dashboard from './components/Dashboard'
import DestinationPanel from './components/DestinationPanel'
import AirlineLinkCard from './components/AirlineLinkCard'
import { Icon } from './components/Icons'
import PopularDestination from './components/PopularDestination'
import { useSettings } from './settings'

const popular = [
  {
    code: 'CDG',
    city: { fr: 'Paris', en: 'Paris' },
    country: { fr: 'France', en: 'France' },
    images: [
      'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1522093007474-d86e9bf7ba6f?auto=format&fit=crop&w=1200&q=80',
    ],
  },
  {
    code: 'LIS',
    city: { fr: 'Lisbonne', en: 'Lisbon' },
    country: { fr: 'Portugal', en: 'Portugal' },
    images: [
      'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1525207934214-58e69a8f8a93?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1548707309-dcebeab9ea9b?auto=format&fit=crop&w=1200&q=80',
    ],
  },
  {
    code: 'FCO',
    city: { fr: 'Rome', en: 'Rome' },
    country: { fr: 'Italie', en: 'Italy' },
    images: [
      'https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1529260830199-42c24126f198?auto=format&fit=crop&w=1200&q=80',
      'https://images.unsplash.com/photo-1529154036614-a60975f5c760?auto=format&fit=crop&w=1200&q=80',
    ],
  },
]

function Header({ user, onLogout }) {
  const navigate = useNavigate()
  const { language, setLanguage, theme, toggleTheme, t } = useSettings()
  return <header className="navbar">
    <Link className="brand" to="/" aria-label={t('homeAria')}><span><Icon name="plane" /></span>TripPilot</Link>
    <nav><Link to="/#popular">{t('destinations')}</Link><Link to="/#results">{t('flights')}</Link></nav>
    <div className="nav-actions">
      <select className="language-select" value={language} onChange={(event) => setLanguage(event.target.value)} aria-label="Language"><option value="fr">FR</option><option value="en">EN</option></select>
      <button className="theme-toggle" onClick={toggleTheme} aria-label={t(theme === 'light' ? 'darkMode' : 'lightMode')} title={t(theme === 'light' ? 'darkMode' : 'lightMode')}><Icon name={theme === 'light' ? 'moon' : 'sun'} /></button>
      <button className="nav-favorite" onClick={() => navigate(user ? '/favorites' : '/login')}><Icon name="heart" /> {t('favorites')}</button>
      {user
        ? <div className="user-menu"><button className="profile-button" onClick={() => navigate('/favorites')}><Icon name="user" /> {user.username}</button><button className="logout" onClick={onLogout}>{t('logout')}</button></div>
        : <button className="profile-button" onClick={() => navigate('/login')}><Icon name="user" /> {t('login')}</button>}
    </div>
  </header>
}

function HomePage({ user, showNotice }) {
  const navigate = useNavigate()
  const { language, t } = useSettings()
  const [form, setForm] = useState({ origin: 'LUX', destination: 'CDG', date: '2026-08-01', passengers: 1 })
  const [airlineLinks, setAirlineLinks] = useState([])
  const [destination, setDestination] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [locationPrompt, setLocationPrompt] = useState(false)
  const [locating, setLocating] = useState(false)

  useEffect(() => {
    const anchor = window.location.hash.slice(1)
    if (anchor) setTimeout(() => document.getElementById(anchor)?.scrollIntoView(), 0)
  }, [])

  useEffect(() => {
    const code = destination?.destination?.code
    if (code) api(`/api/destinations/${encodeURIComponent(code)}?lang=${language}`).then(setDestination).catch(() => {})
  }, [language])

  async function search(event, destinationCode) {
    event?.preventDefault()
    const values = destinationCode ? { ...form, destination: destinationCode } : form
    if (destinationCode) setForm(values)
    setLoading(true)
    setError('')
    setDestination(null)
    setAirlineLinks([])
    try {
      const query = new URLSearchParams({ origin: values.origin, destination: values.destination, date: values.date, adults: values.passengers, lang: language })
      const flightData = await api(`/api/flights/search?${query}`)
      const destinationCodeResolved = flightData.search.destination.code
      const destinationData = await api(`/api/destinations/${encodeURIComponent(destinationCodeResolved)}?lang=${language}`)
      setForm((current) => ({
        ...current,
        origin: flightData.search.origin.code,
        destination: destinationCodeResolved,
      }))
      setAirlineLinks(flightData.airlineLinks || [])
      setDestination(destinationData)
      setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (err) {
      setError(err.message)
      setAirlineLinks([])
    } finally {
      setLoading(false)
    }
  }

  async function requireUser(action) {
    if (!user) {
      navigate('/login')
      return
    }
    try {
      await action()
      showNotice(t('addedFavorite'))
    } catch (err) {
      showNotice(err.message)
    }
  }

  const favoriteDestination = (item) => requireUser(() => api('/api/favorites/destinations', { method: 'POST', body: item }))

  async function detectNearestAirport() {
    setLocating(true)
    try {
      if (!navigator.geolocation) throw new Error(t('locationUnavailable'))
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: false,
          timeout: 10000,
          maximumAge: 300000,
        })
      })
      const data = await api('/api/location/nearest-airport', {
        method: 'POST',
        body: {
          consent: true,
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        },
      })
      setForm((current) => ({ ...current, origin: data.airport.code }))
      showNotice(t('locationFound', { code: data.airport.code, distance: data.airport.distanceKm }))
      setLocationPrompt(false)
    } catch (locationError) {
      showNotice(locationError.message || t('locationUnavailable'))
    } finally {
      setLocating(false)
    }
  }

  return <main id="top">
    <section className="hero">
      <div className="hero-glow"></div>
      <div className="hero-content container">
        <span className="hero-tag"><Icon name="sparkles" /> {t('heroTag')}</span>
        <h1>{t('heroLine1')}<br /><em>{t('heroLine2')}</em></h1>
        <p>{t('heroText')}</p>
        <form className="search-box" onSubmit={search}>
          <AirportAutocomplete label={t('departure')} icon="plane" value={form.origin} onChange={(origin) => setForm({ ...form, origin })} />
          <button type="button" className="swap" onClick={() => setForm({ ...form, origin: form.destination, destination: form.origin })}>⇄</button>
          <AirportAutocomplete label={t('destination')} value={form.destination} onChange={(destination) => setForm({ ...form, destination })} />
          <label><span>{t('departureDate')}</span><input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} required /></label>
          <label><span>{t('travelers')}</span><select value={form.passengers} onChange={(event) => setForm({ ...form, passengers: event.target.value })}><option value="1">{t('traveler1')}</option><option value="2">{t('travelerN', { count: 2 })}</option><option value="3">{t('travelerN', { count: 3 })}</option><option value="4">{t('travelerN', { count: 4 })}</option></select></label>
          <button className="search-button" disabled={loading}><Icon name="search" /> {loading ? t('searching') : t('search')}</button>
        </form>
        <div className="location-control">
          {!locationPrompt
            ? <button type="button" className="location-button" onClick={() => setLocationPrompt(true)}><Icon name="map" /> {t('useLocation')}</button>
            : <div className="location-consent"><p>{t('locationConsent')}</p><div><button type="button" className="secondary-button" onClick={() => setLocationPrompt(false)}>{t('cancel')}</button><button type="button" className="primary-button" onClick={detectNearestAirport} disabled={locating}>{locating ? t('loading') : t('allowLocation')}</button></div></div>}
        </div>
        <div className="trust-row"><span>✓ {t('noFees')}</span><span>✓ {t('secureData')}</span><span>✓ {t('syncedFavorites')}</span></div>
      </div>
    </section>

    <section className="popular container" id="popular">
      <div className="section-heading"><div><span className="eyebrow">{t('inspiration')}</span><h2>{t('whereNext')}</h2></div><p>{t('popularText')}</p></div>
      <div className="popular-grid">{popular.map((place) => <PopularDestination key={place.code} place={place} onSelect={(code) => search(null, code)} />)}</div>
    </section>

    <section className="results container" id="results">
      {error && <div className="error-banner">{error}</div>}
      {!!airlineLinks.length && <><div className="section-heading"><div><span className="eyebrow">{t('bestOptions')}</span><h2>{t('flights')} {form.origin} → {form.destination}</h2></div><div className="live-result"><span>{t('liveOffers')}</span><p>{t('noFlights')}</p></div></div><div className="airline-link-list">{airlineLinks.map((airline) => <AirlineLinkCard key={airline.code} airline={airline} />)}</div></>}
    </section>
    {destination && <div className="container"><DestinationPanel data={destination} onFavorite={favoriteDestination} /></div>}
  </main>
}

function FavoritesPage({ user, checkingUser, showNotice }) {
  const navigate = useNavigate()
  const { t } = useSettings()
  const [favorites, setFavorites] = useState({ destinations: [], flights: [] })

  useEffect(() => {
    if (user) {
      api('/api/favorites').then(setFavorites).catch((error) => showNotice(error.message))
    }
  }, [user])

  if (checkingUser) return <main className="page-loader">{t('loading')}</main>
  if (!user) return <Navigate to="/login" replace />

  async function removeFavorite(type, id) {
    try {
      await api(`/api/favorites/${type}/${id}`, { method: 'DELETE' })
      const key = type === 'flight' ? 'flights' : 'destinations'
      setFavorites((current) => ({ ...current, [key]: current[key].filter((item) => item.id !== id) }))
    } catch (error) {
      showNotice(error.message)
    }
  }

  return <Dashboard favorites={favorites} onDelete={removeFavorite} onClose={() => navigate('/')} />
}

export default function App() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [checkingUser, setCheckingUser] = useState(true)
  const [notice, setNotice] = useState('')
  const { t } = useSettings()

  useEffect(() => {
    api('/api/auth/me')
      .then(({ user: current }) => setUser(current))
      .catch(() => {})
      .finally(() => setCheckingUser(false))
  }, [])

  function showNotice(message) {
    setNotice(message)
    setTimeout(() => setNotice(''), 3000)
  }

  async function logout() {
    await api('/api/auth/logout', { method: 'POST' })
    setUser(null)
    navigate('/')
  }

  return <>
    <Header user={user} onLogout={logout} />
    <Routes>
      <Route path="/" element={<HomePage user={user} showNotice={showNotice} />} />
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <AuthPage mode="login" onAuthenticated={setUser} />} />
      <Route path="/register" element={user ? <Navigate to="/" replace /> : <AuthPage mode="register" onAuthenticated={setUser} />} />
      <Route path="/favorites" element={<FavoritesPage user={user} checkingUser={checkingUser} showNotice={showNotice} />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
    <footer><div className="container"><Link className="brand" to="/"><span><Icon name="plane" /></span>TripPilot</Link><p>{t('footerTagline')}</p><small>{t('footerDemo')}</small></div></footer>
    {notice && <div className="toast">{notice}</div>}
  </>
}
