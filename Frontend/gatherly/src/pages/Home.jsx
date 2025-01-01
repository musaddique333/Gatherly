import React, {useContext} from "react";
import EventCard from "../components/EventCard";
import { Button } from "@mui/material";
import { PlusCircle } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import {useNavigate} from "react-router-dom";

const Home = () => {

  const {isAuthenticated} = useContext(AuthContext);
  const navigate = useNavigate();

  const sampleEvents = [
    {
      title: "React Meetup",
      date: "2024-12-31T18:00:00",
      description: "Learn about React and network with fellow developers!",
      location: "Dublin, Ireland",
      isOnline: false,
      tags: ["React", "JavaScript", "Meetup"],
      organizerEmail: "organizer@meetup.com",
    },
    {
      title: "Web Development Bootcamp",
      date: "2024-12-30T10:00:00",
      description: "Master web development in one day!",
      location: "Online",
      isOnline: true,
      tags: ["HTML", "CSS", "JavaScript"],
      organizerEmail: "bootcamp@webdev.com",
    },
    {
      title: "Tech Conference 2024",
      date: "2024-12-28T09:00:00",
      description: "Explore the latest in tech at this year's biggest conference.",
      location: "San Francisco, CA",
      isOnline: false,
      tags: ["Tech", "Conference", "Networking"],
      organizerEmail: "info@techconf.com",
    },
    {
      title: "Web Development Bootcamp",
      date: "2024-12-30T10:00:00",
      description: "Master web development in one day!",
      location: "Online",
      isOnline: true,
      tags: ["HTML", "CSS", "JavaScript"],
      organizerEmail: "bootcamp@webdev.com",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center mb-12">
          <div className="w-full flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900">
              Upcoming Events
            </h1>
            <Button 
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center gap-2"
              onClick={() => navigate("/user/create-event")}
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
          {sampleEvents.map((event, index) => (
            <div key={index} className="transform transition duration-300 hover:-translate-y-1 hover:shadow-xl">
              <EventCard eventdata={event} />
            </div>
          ))}
        </div>

        {sampleEvents.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No upcoming events at the moment</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;