package org.ourstories.services
{
    import org.ourstories.models.FlvModel;
    
    
    /**
     * FlvService communicates with the "flv" service.
     */
    public class FlvService implements IFlvService
    {
        
        public function ping(flvModel:FlvModel):Operation
        {
            return AmfOperation.ping(flvModel);
        }
        public function getId(flvModel:FlvModel):Operation
        {
            return AmfOperation.getId(flvModel);
        }
        public function getIdSig(flvModel:FlvModel):Operation
        {
            return AmfOperation.getIdSig(flvModel);
        }
        public function setStatus(flvModel:FlvModel):Operation
        {
            return AmfOperation.setStatus(flvModel);
        }
        public function setStatusType(flvModel:FlvModel):Operation
        {
            return AmfOperation.setStatusType(flvModel);
        }
        public function linkFlvToStory(flvModel:FlvModel):Operation
        {
            return AmfOperation.linkFlvToStory(flvModel);
        }
        public function dtrace(flvModel:FlvModel):Operation
        {
            return AmfOperation.dtrace(flvModel);
        }
        

    }
}