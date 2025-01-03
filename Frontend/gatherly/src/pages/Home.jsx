import React, { useState, useEffect, useContext } from "react";
import EventCard from "../components/EventCard";
import { Button } from "@mui/material";
import { PlusCircle } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { eventAxiosInstance } from "../axiosInstance";
import Swal from "sweetalert2";

const Home = () => {
  const { isAuthenticated, userId } = useContext(AuthContext);
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);

  // Function to determine which data to set based on authentication and userId
  function which_data_to_set() {
    if (!isAuthenticated) {

      eventAxiosInstance
        .get("/event/all")
        .then((response) => {
          const newEvents = response.data.map((event) => ({ ...event, isMember: false }));
          setEvents(newEvents);
        })
        .catch((error) => {
          console.log(error);
        });
    } else if (isAuthenticated) {

      eventAxiosInstance
        .get("/event/", {
          params: {
            user_email: userId,
          },
        })
        .then((response) => {
          const userEvents = response.data;
          // Directly set the events with user-specific data
          const updatedEvents = userEvents.map((userEvent) => {
            return { ...userEvent, isMember: true };
          });
          setEvents((prevEvents) =>
            prevEvents.map((event) => {
              const matchedEvent = updatedEvents.find((userEvent) => userEvent.id === event.id);
              if (matchedEvent) {
                return matchedEvent;
              }
              return event;
            })
          );
        })
        
        .catch((error) => {
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Something went wrong!",
          });
        });
    }
  }


  useEffect(() => {
    which_data_to_set();
  }, [isAuthenticated, userId]);

  
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center mb-12">
          <div className="w-full flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900">Upcoming Events</h1>
            <Button
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center gap-2"
              onClick={() => navigate("/create-event")}
            >
              <PlusCircle className="w-5 h-5" />
              Create Event
            </Button>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl">
            Discover and join exciting tech events happening around the world
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {events.map((event, index) => (
            <div key={index} className="transform transition duration-300 hover:-translate-y-1 hover:shadow-xl">
              <EventCard eventdata={event} />
            </div>
          ))}
        </div>

        {events.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No upcoming events at the moment</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
