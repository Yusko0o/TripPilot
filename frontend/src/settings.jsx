import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const messages = {
  fr: {
    destinations: 'Destinations', flights: 'Vols', favorites: 'Favoris', login: 'Se connecter', logout: 'Quitter',
    homeAria: 'Retour à l’accueil', darkMode: 'Activer le mode sombre', lightMode: 'Activer le mode clair',
    heroTag: 'Le voyage, simplifié', heroLine1: 'Tout votre voyage.', heroLine2: 'Une seule recherche.',
    heroText: 'Comparez vos vols, anticipez la météo et découvrez les meilleures adresses de votre destination.',
    departure: 'Départ', destination: 'Destination', airportPlaceholder: 'Ville ou aéroport', departureDate: 'Date de départ',
    travelers: 'Voyageurs', traveler1: '1 voyageur', travelerN: '{count} voyageurs', searching: 'Recherche…', search: 'Rechercher',
    noFees: 'Aucun frais caché', secureData: 'Données sécurisées', syncedFavorites: 'Favoris synchronisés',
    inspiration: 'Inspirations du moment', whereNext: 'Où partons-nous ensuite ?',
    popularText: 'Des villes accessibles depuis Luxembourg, choisies pour une escapade mémorable.', explore: 'Explorer',
    bestOptions: 'Meilleures options', resultsHint: '{count} résultats · cliquez pour ouvrir le site de la compagnie',
    addedFavorite: 'Ajouté à tes favoris', loading: 'Chargement…',
    discover: 'Découvrir la destination', save: 'Enregistrer', humidity: 'Humidité', wind: 'Vent',
    selectedStays: 'Séjours sélectionnés', topHotels: 'Top 10 des hôtels', demoData: 'Données de démonstration',
    from: 'À partir de', night: 'nuit', viewHotel: 'Voir l’hôtel', localExperiences: 'À vivre sur place',
    topActivities: '5 activités incontournables', viewActivity: 'Voir l’activité',
    perPerson: 'par personne', direct: 'Direct', stop: '{count} escale', stops: '{count} escales', favoriteFlight: 'Ajouter le vol aux favoris',
    personalSpace: 'Espace personnel', savedTrips: 'Mes voyages enregistrés', backSearch: 'Retour à la recherche',
    noFavorites: 'Aucun favori pour le moment', noFavoritesText: 'Ajoute un vol ou une destination depuis la recherche.', delete: 'Supprimer',
    authTag: 'Ton voyage, bien organisé', authTitle1: 'Reprends la route', authTitle2: 'là où tu l’avais laissée.',
    authText: 'Retrouve tes vols, tes destinations et toutes tes idées de voyage au même endroit.',
    welcomeBack: 'Bon retour parmi nous', createAccount: 'Créer ton compte', loginText: 'Connecte-toi pour retrouver tes voyages.',
    registerText: 'Quelques secondes suffisent pour commencer.', name: 'Nom', email: 'Adresse e-mail', password: 'Mot de passe',
    passwordHint: '10 caractères minimum, avec au moins une lettre et un chiffre.', oneMoment: 'Un instant…',
    noAccount: 'Pas encore de compte ?', hasAccount: 'Tu as déjà un compte ?', createAccountLink: 'Créer un compte',
    footerTagline: 'Votre prochain voyage commence ici.', footerDemo: 'Prototype pédagogique — les prix et recommandations affichés sont des données de démonstration.',
    useLocation: 'Utiliser mon aéroport le plus proche', locationConsent: 'Ton navigateur va demander l’autorisation d’utiliser ta position pour calculer l’aéroport le plus proche. TripPilot ne conserve pas ta position sur le serveur.',
    allowLocation: 'Autoriser', cancel: 'Annuler', locationFound: 'Aéroport le plus proche : {code} ({distance} km)',
    liveOffers: 'Recherche de vols', noFlights: 'Compare le trajet prérempli ou continue sur le site officiel d’une compagnie pour voir les horaires et prix disponibles.', liveWeather: 'Météo en direct',
    continueAirline: 'Voir les vols', locationUnavailable: 'La position n’est pas disponible ou l’autorisation a été refusée.',
    weatherUnavailable: 'Météo indisponible', weatherTryAgain: 'Réessaie dans quelques instants.',
  },
  en: {
    destinations: 'Destinations', flights: 'Flights', favorites: 'Favorites', login: 'Sign in', logout: 'Sign out',
    homeAria: 'Back to home', darkMode: 'Enable dark mode', lightMode: 'Enable light mode',
    heroTag: 'Travel, simplified', heroLine1: 'Your entire trip.', heroLine2: 'One simple search.',
    heroText: 'Compare flights, check the weather and discover the best places at your destination.',
    departure: 'From', destination: 'Destination', airportPlaceholder: 'City or airport', departureDate: 'Departure date',
    travelers: 'Travelers', traveler1: '1 traveler', travelerN: '{count} travelers', searching: 'Searching…', search: 'Search',
    noFees: 'No hidden fees', secureData: 'Secure data', syncedFavorites: 'Synced favorites',
    inspiration: 'Trending inspiration', whereNext: 'Where should we go next?',
    popularText: 'Cities within easy reach of Luxembourg, selected for a memorable getaway.', explore: 'Explore',
    bestOptions: 'Best options', resultsHint: '{count} results · click to open the airline website',
    addedFavorite: 'Added to your favorites', loading: 'Loading…',
    discover: 'Discover the destination', save: 'Save', humidity: 'Humidity', wind: 'Wind',
    selectedStays: 'Selected stays', topHotels: 'Top 10 hotels', demoData: 'Demo data',
    from: 'From', night: 'night', viewHotel: 'View hotel', localExperiences: 'Things to experience',
    topActivities: '5 must-do activities', viewActivity: 'View activity',
    perPerson: 'per person', direct: 'Direct', stop: '{count} stop', stops: '{count} stops', favoriteFlight: 'Add flight to favorites',
    personalSpace: 'Personal space', savedTrips: 'My saved trips', backSearch: 'Back to search',
    noFavorites: 'No favorites yet', noFavoritesText: 'Add a flight or destination from the search page.', delete: 'Delete',
    authTag: 'Your trip, well organized', authTitle1: 'Pick up your journey', authTitle2: 'right where you left it.',
    authText: 'Find your flights, destinations and travel ideas in one place.',
    welcomeBack: 'Welcome back', createAccount: 'Create your account', loginText: 'Sign in to access your saved trips.',
    registerText: 'It only takes a few seconds to get started.', name: 'Name', email: 'Email address', password: 'Password',
    passwordHint: 'At least 10 characters, including one letter and one number.', oneMoment: 'One moment…',
    noAccount: 'No account yet?', hasAccount: 'Already have an account?', createAccountLink: 'Create an account',
    footerTagline: 'Your next journey starts here.', footerDemo: 'Educational prototype — displayed prices and recommendations are demo data.',
    useLocation: 'Use my nearest airport', locationConsent: 'Your browser will ask permission to use your location to calculate the nearest airport. TripPilot does not store your location on the server.',
    allowLocation: 'Allow', cancel: 'Cancel', locationFound: 'Nearest airport: {code} ({distance} km)',
    liveOffers: 'Flight search', noFlights: 'Compare the pre-filled route or continue to an airline’s official website to see available schedules and prices.', liveWeather: 'Live weather',
    continueAirline: 'View flights', locationUnavailable: 'Location is unavailable or permission was denied.',
    weatherUnavailable: 'Weather unavailable', weatherTryAgain: 'Please try again in a moment.',
  },
}

const SettingsContext = createContext(null)

export function SettingsProvider({ children }) {
  const [language, setLanguage] = useState(() => localStorage.getItem('trippilot-language') || 'fr')
  const [theme, setTheme] = useState(() => localStorage.getItem('trippilot-theme') || 'light')

  useEffect(() => {
    document.documentElement.lang = language
    localStorage.setItem('trippilot-language', language)
  }, [language])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('trippilot-theme', theme)
  }, [theme])

  const value = useMemo(() => ({
    language,
    setLanguage,
    theme,
    toggleTheme: () => setTheme((current) => current === 'light' ? 'dark' : 'light'),
    t: (key, variables = {}) => {
      let text = messages[language][key] || messages.fr[key] || key
      Object.entries(variables).forEach(([name, value]) => { text = text.replace(`{${name}}`, value) })
      return text
    },
  }), [language, theme])

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>
}

export function useSettings() {
  return useContext(SettingsContext)
}
