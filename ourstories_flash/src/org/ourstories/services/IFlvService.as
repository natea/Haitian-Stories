package org.ourstories.services
{
    import org.ourstories.models.FlvModel;
    
    public interface IFlvService
    {
        
        function ping(flvModel:FlvModel):Operation;
        function getId(flvModel:FlvModel):Operation;
        function getIdSig(flvModel:FlvModel):Operation;
        function setStatus(flvModel:FlvModel):Operation;
        function setStatusType(flvModel:FlvModel):Operation;
        function linkFlvToStory(flvModel:FlvModel):Operation;
        function dtrace(flvModel:FlvModel):Operation;
        
    }
}