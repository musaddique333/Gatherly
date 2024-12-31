import React from "react";

import EventCard from "../components/EventCard";

const Home = () => {

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
    ];

    return (
        <div className="min-h-screen bg-gray-100 py-8">
        <div className="container mx-auto px-4 w-3/4">
          <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">
            Upcoming Events
          </h1>
          <div className="flex flex-col gap-6">
            {sampleEvents.map((event, index) => (
              <EventCard key={index} eventdata={event} />
            ))}
          </div>
        </div>
      </div>
      );
};

export default Home;