import { useEffect, useState } from 'react'
import { Icon } from './Icons'
import { useSettings } from '../settings'

export default function PopularDestination({ place, onSelect }) {
  const [imageIndex, setImageIndex] = useState(0)
  const { language, t } = useSettings()

  useEffect(() => {
    const interval = setInterval(() => {
      setImageIndex((current) => (current + 1) % place.images.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [place.images.length])

  return <button className="destination-card" onClick={() => onSelect(place.code)}>
    {place.images.map((image, index) => <span key={image} className={`destination-slide ${index === imageIndex ? 'active' : ''}`} style={{ backgroundImage: `linear-gradient(0deg, rgba(3,16,24,.85), transparent 65%), url(${image})` }} />)}
    <span className="destination-country">{place.country[language]}</span>
    <strong>{place.city[language]}</strong>
    <small>{t('explore')} <Icon name="arrow" /></small>
    <span className="carousel-dots" aria-hidden="true">{place.images.map((_, index) => <i key={index} className={index === imageIndex ? 'active' : ''} />)}</span>
  </button>
}
