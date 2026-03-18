import React, { useEffect, useState, useMemo } from "react"

import { MapContainer, TileLayer, GeoJSON } from "react-leaflet"

import "leaflet/dist/leaflet.css"

import RAW_COMMUNITY_AREAS from "../../../data/raw/community-areas.geojson"

function YearSelect({ setFilterVal }) {
  const startYear = 2026
  const years = [...Array(11).keys()].map((increment) => {
    return startYear - increment
  })
  const options = years.map((year) => {
    return (
      <option value={year} key={year}>
        {year}
      </option>
    )
  })

  return (
    <>
      <label htmlFor="yearSelect" className="fs-3">
        Filter by year:{" "}
      </label>
      <select
        id="yearSelect"
        className="form-select form-select-lg mb-3"
        onChange={(e) => setFilterVal(e.target.value)}
      >
        {options}
      </select>
    </>
  )
}

export default function RestaurantPermitMap() {
  const communityAreaColors = ["#eff3ff", "#bdd7e7", "#6baed6", "#2171b5"]

  const [currentYearData, setCurrentYearData] = useState([])
  const [year, setYear] = useState(2026)
  const [error, setError] = useState(null)

  const yearlyDataEndpoint = `/map-data/?year=${year}`

  useEffect(() => {
    fetch(yearlyDataEndpoint)
      .then((res) => {
        if(!res.ok){
          throw new Error(`Failed to fetch data for year ${year} (status: ${res.status})`)
        }
        return res.json()
      })
      .then((data) => {
        setCurrentYearData(data)
        setError(null)
      })
      .catch((error) => {
        console.log(error.message)
        setError(error.message)
      })
  }, [year])

  const {totalPermits, maxNumPermits} = useMemo(()=>{
    return currentYearData.reduce(
      (stats, communityArea) => {
        const permits = communityArea.num_permits || 0

        stats.totalPermits += permits
        stats.maxNumPermits = Math.max(stats.maxNumPermits, permits)

        return stats
      },
      { totalPermits: 0, maxNumPermits:0}
    )

  }, [currentYearData])

  const permitsByCommunity = useMemo(() => {
    return currentYearData.reduce((permitsByCommunity, communityAreaData) => {
      permitsByCommunity[communityAreaData.name] = communityAreaData.num_permits || 0
      return permitsByCommunity
    }, {})

  }, [currentYearData])


  function getColor(percentageOfPermits) {
    const colorIndex = Math.min(
      communityAreaColors.length - 1,
      Math.floor(percentageOfPermits * communityAreaColors.length)
    )
    return communityAreaColors[colorIndex]
  }

  function setAreaInteraction(feature, layer) {
    const community = feature.properties.community
    const communityPermits = permitsByCommunity[community] || 0
    const communityPermitPercentage = maxNumPermits > 0 ? communityPermits / maxNumPermits : 0
    const fillColor = getColor(communityPermitPercentage)

    layer.setStyle({
      fillColor: fillColor,
      fillOpacity: 0.65,
    })
    
    const popupContent = `
    <strong>${community}</strong><br/>
    Year: ${year}<br/>
    Restaurant permits: ${communityPermits}
  `

    layer.bindPopup(popupContent)

    layer.on("mouseover", () => {
      layer.openPopup()
    })

    layer.on("mouseout", () => {
      layer.closePopup()
    })
  }

  return (
    <>
      {error && (
        <div className="alert alert-danger mt-3" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}
      <YearSelect filterVal={year} setFilterVal={setYear} />
      <p className="fs-4">
        Restaurant permits issued this year: {totalPermits}
      </p>
      <p className="fs-4">
        Maximum number of restaurant permits in a single area:
        {maxNumPermits}
      </p>
      <MapContainer
        id="restaurant-map"
        center={[41.88, -87.62]}
        zoom={10}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png"
        />
        {currentYearData.length > 0 ? (
          <GeoJSON
            data={RAW_COMMUNITY_AREAS}
            onEachFeature={setAreaInteraction}
            key={maxNumPermits}
          />
        ) : null}
      </MapContainer>
    </>
  )
}
