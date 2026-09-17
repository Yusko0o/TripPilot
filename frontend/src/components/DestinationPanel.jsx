import { Icon } from './Icons'
import { useSettings } from '../settings'

export default function DestinationPanel({ data, onFavorite }) {
  const { destination, weather, hotels, activities } = data
  const { t } = useSettings()
  return <section className="destination-section" id="destination">
    <div className="destination-hero" style={{ backgroundImage: `linear-gradient(90deg, rgba(5,20,30,.83), rgba(5,20,30,.08)), url(${destination.image})` }}>
      <div>
        <span className="eyebrow light">{t('discover')}</span>
        <h2>{destination.city}</h2>
        <p>{destination.country} · {destination.code}</p>
        <button className="glass-button" onClick={() => onFavorite(destination)}><Icon name="heart" /> {t('save')}</button>
      </div>
      {weather?.available !== false
        ? <div className="weather-card">
          <Icon name="cloud" size={32} />
          <strong>{weather.temperature}°</strong>
          <span>{weather.condition}</span>
          <small>{t('humidity')} {weather.humidity}% · {t('wind')} {weather.wind} km/h<br /><b className="live-weather">● {t('liveWeather')}</b></small>
        </div>
        : <div className="weather-card weather-unavailable">
          <Icon name="cloud" size={32} />
          <strong>—°</strong>
          <span>{t('weatherUnavailable')}</span>
          <small>{t('weatherTryAgain')}</small>
        </div>}
    </div>

    <div className="section-heading">
      <div><span className="eyebrow">{t('selectedStays')}</span><h2>{t('topHotels')}</h2></div>
      <span className="demo-badge">{t('demoData')}</span>
    </div>
    <div className="hotel-grid">
      {hotels.map((hotel, index) => <article className="hotel-card" key={hotel.id}>
        <span className="rank">#{index + 1}</span>
        <div className="hotel-icon"><Icon name="hotel" /></div>
        <h3>{hotel.name}</h3>
        <div className="rating">★ {hotel.rating}</div>
        <p>{t('from')} <strong>{hotel.price} €</strong> / {t('night')}</p>
        <a className="external-link" href={hotel.websiteUrl} target="_blank" rel="noopener noreferrer">{t('viewHotel')} <Icon name="external" size={15} /></a>
      </article>)}
    </div>

    <div className="section-heading activities-title">
      <div><span className="eyebrow">{t('localExperiences')}</span><h2>{t('topActivities')}</h2></div>
    </div>
    <div className="activity-list">
      {activities.map((activity, index) => <article key={activity.name}>
        <span className="activity-number">0{index + 1}</span>
        <div><small>{activity.category}</small><h3>{activity.name}</h3></div>
        <span>{activity.duration}</span>
        <a className="activity-link" href={activity.websiteUrl} target="_blank" rel="noopener noreferrer" aria-label={t('viewActivity')}><Icon name="external" /></a>
      </article>)}
    </div>
  </section>
}
