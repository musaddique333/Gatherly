import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Button } from "@mui/material";
import { Event } from "@mui/icons-material";
import { eventAxiosInstance } from "../axiosInstance";
import Swal from 'sweetalert2';
import { AuthContext } from '../context/AuthContext';

const EventCard = ({eventdata}) => {
  const formatDate = (dateString) => new Date(dateString).toLocaleString();
  const {userId} = useContext(AuthContext);

  const onJoinEvent = () => {
    eventAxiosInstance.get("/event/" + eventdata.id, {
      params: {
        user_email: userId
      }
    })
      .then((response) => {
      console.log(response);
      if (response.status === 200) {
        Swal.fire({
          icon: "success",
          title: "Joined Event",
          text: "Hooray! Organizer will shortly add you to the event!",
        });
        
      }
    })
    .catch((error) => {
      console.log(error);
    });
  };

  return (
    <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-4">
      <div className="px-6 py-4">
        <div className="flex items-center mb-2">
          {/* Optional Icon */}
          <Event className="text-blue-500 mr-2" />
          <h2 className="font-bold text-xl text-gray-800">{eventdata.title}</h2>
        </div>
        <p className="text-gray-600 text-sm mb-2">
          📅 {formatDate(eventdata.date)}
        </p>
        <p className="text-gray-700 text-base mb-2">
          {eventdata.description || "No description provided."}
        </p>
        <p className="text-gray-600 text-sm mb-2">
          📍 {eventdata.isOnline ? "Online" : eventdata.location || "Location not specified."}
        </p>
        {eventdata.tags && eventdata.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {eventdata.tags.map((tag, index) => (
              <span
                key={index}
                className="bg-blue-500 text-white text-xs px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
        <p className="text-gray-500 text-xs">Organizer: {eventdata.organizer_email}</p>
      </div>
      <div className="px-6 py-4">
        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={onJoinEvent}
        >
          Join Event
        </Button>
      </div>
    </div>
  );
};

// Define PropTypes for the component
EventCard.propTypes = {
  eventdata: PropTypes.object.isRequired
};

export default EventCard;
