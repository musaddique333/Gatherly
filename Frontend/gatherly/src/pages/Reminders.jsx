import React, {useState, useEffect, useCallback, useContext} from "react";
import ReminderCard from "../components/Remindercard";
import { Button } from "@mui/material";
import { PlusCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { eventAxiosInstance } from "../axiosInstance";
import { AuthContext } from "../context/AuthContext";

const Reminders = () => {
    
    const [reminders, setReminders] = useState([]);
    const navigate = useNavigate();
    const {userId} = useContext(AuthContext);

    useEffect(() => {
        eventAxiosInstance
        .get("/reminder/", {
            params: {
                user_email: localStorage.getItem("userId")
            }
        })
        .then ((response) => {
            setReminders(response.data);
        })
        .catch((error) => {
            console.log(error);
        })
    }, []);

      const fetchReminders = useCallback(() => {
    
        if(!userId)
        {
          return;
        }
        eventAxiosInstance
        .get("/reminder/", {
            params: {
                user_email: userId
            }
        })
        .then ((response) => {
            setReminders(response.data);
        })
        .catch((error) => {
            console.log(error);
        })
      }, [userId]);

      useEffect(() => {
        fetchReminders();
      }, [fetchReminders])

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="flex flex-col items-center mb-12">
              <div className="w-full flex justify-between items-center mb-8">
                <h1 className="text-4xl font-bold text-gray-900">
                  Upcoming Reminders
                </h1>
                <Button 
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center gap-2"
                  onClick={() => navigate("/user/reminders/add-reminder")}
                >
                  <PlusCircle className="w-5 h-5" />
                  Create Reminder
                </Button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {reminders.map((reminder, index) => (
                <div key={index} className="transform transition duration-300 hover:-translate-y-1 hover:shadow-xl">
                  <ReminderCard reminderdata={reminder} />
                </div>
              ))}
            </div>
    
            {reminders.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No upcoming reminders at the moment</p>
              </div>
            )}
          </div>
        </div>
      );
};

export default Reminders;