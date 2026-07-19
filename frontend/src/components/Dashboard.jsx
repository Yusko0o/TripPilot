import { Icon } from './Icons'
import { useSettings } from '../settings'

export default function Dashboard({ favorites, onDelete, onClose }) {
  const empty = !favorites.destinations.length && !favorites.flights.length
  const { t } = useSettings()
  return <section className="dashboard container">
    <div className="section-heading">
      <div><span className="eyebrow">{t('personalSpace')}</span><h1>{t('savedTrips')}</h1></div>
      <button className="secondary-button" onClick={onClose}>{t('backSearch')}</button>
    </div>
    {empty && <div className="empty-state"><Icon name="heart" size={38} /><h2>{t('noFavorites')}</h2><p>{t('noFavoritesText')}</p></div>}
    {!!favorites.destinations.length && <><h2 className="dashboard-subtitle">{t('destinations')}</h2><div className="saved-grid">
      {favorites.destinations.map((item) => <article className="saved-destination" key={item.id} style={item.image ? { backgroundImage: `linear-gradient(rgba(0,0,0,.15), rgba(0,0,0,.72)), url(${item.image})` } : {}}>
        <div><small>{item.country}</small><h3>{item.city}</h3></div>
        <button className="icon-button" onClick={() => onDelete('destination', item.id)} aria-label={t('delete')}><Icon name="trash" /></button>
      </article>)}
    </div></>}
    {!!favorites.flights.length && <><h2 className="dashboard-subtitle">{t('flights')}</h2><div className="saved-flights">
      {favorites.flights.map((item) => <article key={item.id}><strong>{item.from} <Icon name="arrow" /> {item.to}</strong><span>{item.provider} · {item.flightNumber}</span><b>{item.price} €</b><button className="icon-button" onClick={() => onDelete('flight', item.id)}><Icon name="trash" /></button></article>)}
    </div></>}
  </section>
}
