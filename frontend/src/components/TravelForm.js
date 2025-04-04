import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown'; // Ensure this is installed
import './TravelForm.css';

const TravelForm = () => {
  const [formData, setFormData] = useState({
    from_city: '',
    to_city: '',
    departure_date: '',
    return_date: '',
    num_adults: 1,
    num_children: 0,
    children_ages: [], // Will be populated dynamically based on num_children
    min_price: 5000,
    max_price: 30000,
    budget: 50000,
    days: 0, // Will be calculated dynamically
    from_station: '',
    to_station: '',
  });
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Calculate trip duration when departure_date or return_date changes
  useEffect(() => {
    if (formData.departure_date && formData.return_date) {
      const departure = new Date(formData.departure_date);
      const returnDate = new Date(formData.return_date);
      if (returnDate >= departure) {
        const diffTime = Math.ceil((returnDate - departure) / (1000 * 60 * 60 * 24)) + 1; // Include both days
        setFormData((prev) => ({
          ...prev,
          days: diffTime,
        }));
      } else {
        setError('Return date must be after departure date.');
      }
    }
  }, [formData.departure_date, formData.return_date]);

  // Handle changes for most input fields
  const handle_Change = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'num_adults' || name === 'num_children' || name === 'min_price' || name === 'max_price' || name === 'budget'
        ? parseInt(value) || 0
        : value,
    }));
  };

  // Handle changes for num_children and initialize children_ages array
  const handleChildrenChange = (e) => {
    const numChildren = parseInt(e.target.value) || 0;
    const newChildrenAges = Array(numChildren).fill(0); // Initialize with zeros
    setFormData((prev) => ({
      ...prev,
      num_children: numChildren,
      children_ages: newChildrenAges,
    }));
  };

  // Handle changes for individual child ages
  const handleChildAgeChange = (index, value) => {
    const newChildrenAges = [...formData.children_ages];
    newChildrenAges[index] = parseInt(value) || 0;
    setFormData((prev) => ({
      ...prev,
      children_ages: newChildrenAges,
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    console.log('Sending form data:', formData); // Debug log
    try {
      const response = await axios.post('http://localhost:8080/generate-itinerary', formData, {
        headers: { 'Content-Type': 'application/json' },
      });
      console.log('Response:', response.data); // Debug log
      setItinerary(response.data.itinerary);
    } catch (error) {
      console.error('Error details:', error.response ? error.response.data : error.message);
      setError('Failed to generate itinerary. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="travel-form-container">
      <h1>Travel Planner</h1>
      <form onSubmit={handleSubmit} className="travel-form">
        {/* From City */}
        <div className="form-group">
          <label htmlFor="from_city">From City</label>
          <input
            id="from_city"
            name="from_city"
            type="text"
            placeholder="e.g., New Delhi"
            value={formData.from_city}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Enter the city you are traveling from.</small>
        </div>

        {/* To City */}
        <div className="form-group">
          <label htmlFor="to_city">To City</label>
          <input
            id="to_city"
            name="to_city"
            type="text"
            placeholder="e.g., Bhopal"
            value={formData.to_city}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Enter your destination city.</small>
        </div>

        {/* Departure Date */}
        <div className="form-group">
          <label htmlFor="departure_date">Departure Date</label>
          <input
            id="departure_date"
            name="departure_date"
            type="date"
            value={formData.departure_date}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Select the date you plan to leave (format: YYYY-MM-DD).</small>
        </div>

        {/* Return Date */}
        <div className="form-group">
          <label htmlFor="return_date">Return Date</label>
          <input
            id="return_date"
            name="return_date"
            type="date"
            value={formData.return_date}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Select the date you plan to return (format: YYYY-MM-DD).</small>
        </div>

        {/* Number of Adults */}
        <div className="form-group">
          <label htmlFor="num_adults">Number of Adults</label>
          <input
            id="num_adults"
            name="num_adults"
            type="number"
            min="1"
            value={formData.num_adults}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Enter the number of adults traveling (minimum 1).</small>
        </div>

        {/* Number of Children */}
        <div className="form-group">
          <label htmlFor="num_children">Number of Children</label>
          <input
            id="num_children"
            name="num_children"
            type="number"
            min="0"
            value={formData.num_children}
            onChange={handleChildrenChange}
            required
          />
          <small className="helper-text">Enter the number of children traveling (0 or more).</small>
        </div>

        {/* Children Ages */}
        {formData.num_children > 0 && (
          <div className="form-group">
            <label>Children Ages</label>
            {Array.from({ length: formData.num_children }).map((_, index) => (
              <div key={index} className="child-age-group">
                <label htmlFor={`child_age_${index}`}>Child {index + 1} Age</label>
                <input
                  id={`child_age_${index}`}
                  type="number"
                  min="0"
                  max="17"
                  value={formData.children_ages[index] || 0}
                  onChange={(e) => handleChildAgeChange(index, e.target.value)}
                  required
                />
                <small className="helper-text">Enter the age of child {index + 1} (0-17).</small>
              </div>
            ))}
          </div>
        )}

        {/* Minimum Price */}
        <div className="form-group">
          <label htmlFor="min_price">Minimum Price (INR)</label>
          <input
            id="min_price"
            name="min_price"
            type="number"
            min="0"
            value={formData.min_price}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Enter the minimum price for hotels (in INR).</small>
        </div>

        {/* Maximum Price */}
        <div className="form-group">
          <label htmlFor="max_price">Maximum Price (INR)</label>
          <input
            id="max_price"
            name="max_price"
            type="number"
            min="0"
            value={formData.max_price}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Enter the maximum price for hotels (in INR).</small>
        </div>

        {/* Budget */}
        <div className="form-group">
          <label htmlFor="budget">Total Budget (INR)</label>
          <input
            id="budget"
            name="budget"
            type="number"
            min="1000"
            value={formData.budget}
            onChange={handle_Change}
            required
          />
          <small className="helper-text">Enter your total budget for the trip (in INR).</small>
        </div>

        {/* Trip Duration (Days) - Display only, calculated automatically */}
        <div className="form-group">
          <label>Trip Duration (Days)</label>
          <input
            id="days"
            name="days"
            type="number"
            min="1"
            value={formData.days}
            readOnly // Make it read-only since it's calculated
          />
          <small className="helper-text">Calculated based on departure and return dates (includes both days).</small>
        </div>

        {/* From Station */}
        <div className="form-group">
          <label htmlFor="from_station">From Station Code</label>
          <input
            id="from_station"
            name="from_station"
            type="text"
            placeholder="e.g., NDLS"
            value={formData.from_station}
            onChange={handle_Change}
          />
          <small className="helper-text">Enter the station code for your departure city (optional, e.g., NDLS for New Delhi).</small>
        </div>

        {/* To Station */}
        <div className="form-group">
          <label htmlFor="to_station">To Station Code</label>
          <input
            id="to_station"
            name="to_station"
            type="text"
            placeholder="e.g., BPL"
            value={formData.to_station}
            onChange={handle_Change}
          />
          <small className="helper-text">Enter the station code for your destination city (optional, e.g., BPL for Bhopal).</small>
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Itinerary'}
        </button>
      </form>

      {/* Error Message */}
      {error && <div className="error-message">{error}</div>}

      {/* Itinerary Display in Markdown */}
      {itinerary && (
        <div className="itinerary-container">
          <h2>Your Travel Itinerary</h2>
          <div className="markdown-content">
            <ReactMarkdown>{itinerary}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

export default TravelForm;