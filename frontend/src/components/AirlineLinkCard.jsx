import { Icon } from './Icons'
import { useSettings } from '../settings'

export default function AirlineLinkCard({ airline }) {
  const { t } = useSettings()
  return <a className="airline-link-card" href={airline.websiteUrl} target="_blank" rel="noopener noreferrer">
    <div className={`airline-mark ${airline.provider.toLowerCase().replace(' ', '-')}`}>{airline.code}</div>
    <div>
      <strong>{airline.provider}</strong>
      <span>{airline.origin} → {airline.destination} · {airline.departureDate}</span>
    </div>
    <span className="airline-continue">{t('continueAirline')} <Icon name="external" /></span>
  </a>
}
