import { useEffect, useId, useRef, useState } from 'react'
import { api } from '../api'
import { Icon } from './Icons'
import { useSettings } from '../settings'

export default function AirportAutocomplete({ label, icon = 'map', value, onChange }) {
  const listId = useId()
  const wrapper = useRef(null)
  const selectedCode = useRef(null)
  const { t } = useSettings()
  const [query, setQuery] = useState(value)
  const [suggestions, setSuggestions] = useState([])
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(-1)

  useEffect(() => {
    if (value !== selectedCode.current) {
      selectedCode.current = null
      setQuery(value)
    }
  }, [value])

  useEffect(() => {
    if (selectedCode.current) {
      setSuggestions([])
      setOpen(false)
      return
    }
    if (query.trim().length < 2) {
      setSuggestions([])
      return
    }
    const controller = new AbortController()
    const timer = setTimeout(() => {
      api(`/api/airports/search?q=${encodeURIComponent(query)}`, { signal: controller.signal })
        .then(({ airports }) => {
          setSuggestions(airports)
          setOpen(airports.length > 0)
          setActive(-1)
        })
        .catch((error) => {
          if (error.name !== 'AbortError') setSuggestions([])
        })
    }, 220)
    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [query])

  useEffect(() => {
    const close = (event) => {
      if (!wrapper.current?.contains(event.target)) setOpen(false)
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [])

  function select(airport) {
    selectedCode.current = airport.code
    setQuery(`${airport.city || airport.name} — ${airport.code}`)
    onChange(airport.code)
    setOpen(false)
  }

  function keyDown(event) {
    if (!open || !suggestions.length) return
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActive((current) => (current + 1) % suggestions.length)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActive((current) => (current <= 0 ? suggestions.length - 1 : current - 1))
    } else if (event.key === 'Enter' && active >= 0) {
      event.preventDefault()
      select(suggestions[active])
    } else if (event.key === 'Escape') {
      setOpen(false)
    }
  }

  return <label className="airport-field" ref={wrapper}>
    <span>{label}</span>
    <div><Icon name={icon} /><input value={query} onChange={(event) => { selectedCode.current = null; setQuery(event.target.value); onChange(event.target.value) }} onFocus={() => suggestions.length && setOpen(true)} onKeyDown={keyDown} placeholder={t('airportPlaceholder')} autoComplete="off" role="combobox" aria-expanded={open} aria-controls={listId} required /></div>
    {open && <ul className="airport-suggestions" id={listId} role="listbox">
      {suggestions.map((airport, index) => <li key={airport.code} className={index === active ? 'active' : ''} role="option" aria-selected={index === active} onMouseDown={(event) => { event.preventDefault(); select(airport) }}>
        <span className="airport-code">{airport.code}</span>
        <span><strong>{airport.city || airport.name}</strong><small>{airport.name} · {airport.country}</small></span>
      </li>)}
    </ul>}
  </label>
}
