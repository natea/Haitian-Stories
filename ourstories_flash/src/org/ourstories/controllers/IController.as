package org.ourstories.controllers
{
    import org.ourstories.models.FlvModel;
    import org.ourstories.services.IFlvService;
    
    public interface IController
    {
        
        // flv actions
        function ping():FlvModel;
        function getId():FlvModel;
        function getIdSig():FlvModel;
        function setStatus(flvModel:FlvModel):FlvModel;
        function setStatusType(flvModel:FlvModel):FlvModel;
        function linkFlvToStory(flvModel:FlvModel):FlvModel;
        function dtrace(flvModel:FlvModel):FlvModel;
                
        
        /**
         * IFlvService reference for controller's use.
         */
        function get flvService():IFlvService;
        function set flvService(value:IFlvService):void;

        /**
         * Bindable message for status messages from any operation.
         */
        function get message():String;
        function set message(value:String):void;
        
    }
    
}