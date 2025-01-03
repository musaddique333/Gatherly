import React, {useState, useContext, useEffect, useCallback} from "react";
import EventCard from "../components/EventCard";
import { Button } from "@mui/material";
import { PlusCircle } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import {useNavigate} from "react-router-dom";
import { eventAxiosInstance } from "../axiosInstance";
import EventCardWithoutJoin from "../components/EventCardWithoutJoin";
import Swal from "sweetalert2";

const UserDashboard = () => {

  const {userId} = useContext(AuthContext);
  const navigate = useNavigate();

  const [events, setEvents] = useState([]);

  const [loading, setLoading] = useState(true);

  // useEffect(() => {
  //     eventAxiosInstance.get("/event/", {
  //       params: {
  //         user_email: userId
  //       }
  //     })
  //     .then((response) => {
  //       setEvents(response.data);
  //     })
  //     .catch((error) => {
  //       Swal.fire({
  //         icon: 'error',
  //         title: 'Oops...',
  //         text: 'Something went wrong!',
  //       })
  //     })
  // }, []);

  const fetchEvents = useCallback(() => {

    if(!userId)
    {
      return;
    }

    eventAxiosInstance
      .get("/event/", {
        params: {
          user_email: userId,
        },
      })
      .then((response) => {
        setEvents(response.data);
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Oops...",
          text: "Something went wrong!",
        });
      });
  }, [userId]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center mb-12">
          <div className="w-full flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900">
              Your Upcoming Events!
            </h1>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {events.map((event, index) => (
            <div key={index} className="transform transition duration-300 hover:-translate-y-1 hover:shadow-xl">
              <EventCardWithoutJoin eventdata={event} />
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

export default UserDashboard;