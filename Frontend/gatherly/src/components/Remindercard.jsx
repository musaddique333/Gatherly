import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Event } from "@mui/icons-material";


const ReminderCard = ({reminderdata}) => {
  const formatDate = (dateString) => new Date(dateString).toLocaleString();

  return (
    <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-4">
      <div className="px-6 py-4">
            <div className="flex items-center mb-2">
            <Event className="text-blue-500 mr-2" />
            <h2 className="font-bold text-xl text-gray-800">{reminderdata.title}</h2>
            </div>
            <p className="text-gray-600 text-sm mb-2">
            📅 {formatDate(reminderdata.date)}
            </p>
            <p className="text-gray-600 text-sm mb-2">
            Reminder Time: 📅 {formatDate(reminderdata.reminder_time)}
            </p>
            <p className = "text-gray-600 text-sm mb-2">
              Event Id: {reminderdata.event_id}
            </p>
        </div>
    </div>
  );
};

ReminderCard.propTypes = {
  reminderdata: PropTypes.object.isRequired
};

export default ReminderCard;

