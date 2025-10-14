export interface Country {
  id: number
  name: string
  iso3: string
  iso2: string
  numeric_code: string
  phone_code: string
  capital: string
  currency: string
  currency_name: string
  currency_symbol: string
  tld: string
  native: string
  region: string
  subregion: string
  latitude: string
  longitude: string
  emoji: string
  hasStates: boolean
}

export interface City {
  id: number
  name: string
  latitude: string
  longitude: string
}

export interface State {
  id: number
  name: string
  state_code: string
  hasCities: boolean
  latitude: string | null
  longitude: string | null
  cities?: City[]
}

export interface StatesData {
  id: number
  states: State[]
}

export interface CitiesData {
  id: number
  states: {
    id: number
    cities: City[]
  }[]
}
